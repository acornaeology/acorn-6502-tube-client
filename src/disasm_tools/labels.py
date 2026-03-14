"""Generate per-label context files for systematic label renaming.

Classifies auto-generated labels (c####, l####, loop_c####, sub_c####)
into five categories and produces context files with assembly excerpts,
inbound references, parent subroutine info, and ready-to-edit rename
templates.

Categories:
  subroutine         JSR/JMP targets or dispatch entries (get subroutine())
  data               l#### byte/string items (rename only)
  internal_loop      loop_c#### backward-branch targets (rename only)
  internal_conditional  c#### referenced only within parent sub (rename only)
  shared_tail        c#### referenced from multiple subs by branch (rename only)
"""

import json
import re
import sys
from pathlib import Path

from disasm_tools.audit import (
    BASE_MEMORY_REGIONS,
    BRANCH_MNEMONICS,
    build_memory_regions,
    load_subroutines,
    region_for_addr,
)
from disasm_tools.asm_extract import build_index, find_line_for_target

AUTO_LABEL_RE = re.compile(
    r"^(c[0-9a-f]+|l[0-9a-f]+|loop_c[0-9a-f]+|sub_c[0-9a-f]+)$"
)

CATEGORY_ORDER = [
    "subroutine",
    "shared_tail",
    "data",
    "internal_loop",
    "internal_conditional",
]


def _collect_auto_labels(items):
    """Return list of (label_name, addr) for all auto-generated labels."""
    results = []
    for item in items:
        for lbl in item.get("labels", []):
            if AUTO_LABEL_RE.match(lbl):
                results.append((lbl, item["addr"]))
        for addr_str, sub_lbls in item.get("sub_labels", {}).items():
            for lbl in sub_lbls:
                if AUTO_LABEL_RE.match(lbl):
                    results.append((lbl, int(addr_str)))
    return results


def _build_target_refs(items):
    """Build addr -> list of referencing items index."""
    refs = {}
    for item in items:
        target = item.get("target")
        if target is not None:
            refs.setdefault(target, []).append(item)
    return refs


def _find_containing_sub_for_addr(addr, sorted_subs, memory_regions):
    """Find the subroutine whose extent contains addr.

    Uses the sorted subroutine list from load_subroutines(). A sub's
    extent runs from its addr to the start of the next sub in the same
    memory region (or to the region end).
    """
    result = None
    result_region = None
    addr_region = region_for_addr(addr, memory_regions)

    for sub in sorted_subs:
        sub_region = region_for_addr(sub["addr"], memory_regions)
        if sub_region != addr_region:
            continue
        if sub["addr"] <= addr:
            result = sub
            result_region = sub_region
        else:
            break
    return result


def _classify_labels(auto_labels, items, target_refs, audit_subs,
                     memory_regions):
    """Classify each auto-generated label into a category.

    Returns list of dicts with keys: name, addr, category, parent_sub,
    inbound_refs (list of {addr, mnemonic, sub_name, cross_sub}).
    """
    items_by_addr = {item["addr"]: item for item in items}
    sorted_subs = sorted(audit_subs, key=lambda s: s["addr"])

    results = []
    for label_name, label_addr in auto_labels:
        parent_sub = _find_containing_sub_for_addr(
            label_addr, sorted_subs, memory_regions)
        parent_name = parent_sub["name"] if parent_sub else None
        parent_addr = parent_sub["addr"] if parent_sub else None

        # Collect all inbound references
        inbound = []
        for ref_item in target_refs.get(label_addr, []):
            ref_sub = _find_containing_sub_for_addr(
                ref_item["addr"], sorted_subs, memory_regions)
            ref_sub_name = ref_sub["name"] if ref_sub else "?"
            ref_sub_addr = ref_sub["addr"] if ref_sub else None
            cross = ref_sub_addr != parent_addr
            inbound.append({
                "addr": ref_item["addr"],
                "mnemonic": ref_item.get("mnemonic", "?"),
                "sub_name": ref_sub_name,
                "sub_addr": ref_sub_addr,
                "cross_sub": cross,
            })

        # Also check the 'references' field on the item itself for
        # data table / pointer references not captured by target
        item_at_label = items_by_addr.get(label_addr)
        ref_addrs_from_target = {r["addr"] for r in inbound}
        if item_at_label:
            for ref_addr in item_at_label.get("references", []):
                if ref_addr not in ref_addrs_from_target:
                    ref_item = items_by_addr.get(ref_addr)
                    if ref_item:
                        ref_sub = _find_containing_sub_for_addr(
                            ref_addr, sorted_subs, memory_regions)
                        ref_sub_name = ref_sub["name"] if ref_sub else "?"
                        ref_sub_addr = ref_sub["addr"] if ref_sub else None
                        cross = ref_sub_addr != parent_addr
                        inbound.append({
                            "addr": ref_addr,
                            "mnemonic": ref_item.get("mnemonic", "data_ref"),
                            "sub_name": ref_sub_name,
                            "sub_addr": ref_sub_addr,
                            "cross_sub": cross,
                        })

        # Sort inbound by address
        inbound.sort(key=lambda r: r["addr"])

        cross_sub_refs = [r for r in inbound if r["cross_sub"]]
        has_jsr_jmp = any(
            r["mnemonic"] in ("jsr", "jmp") for r in cross_sub_refs
        )

        # Classification (check longer prefixes first to avoid
        # loop_c/sub_c matching the shorter l/c prefix)
        if label_name.startswith("sub_c"):
            category = "subroutine"
        elif label_name.startswith("loop_c"):
            category = "internal_loop"
        elif label_name.startswith("l"):
            category = "data"
        elif has_jsr_jmp:
            category = "subroutine"
        elif cross_sub_refs:
            category = "shared_tail"
        else:
            category = "internal_conditional"

        results.append({
            "name": label_name,
            "addr": label_addr,
            "category": category,
            "parent_sub_name": parent_name,
            "parent_sub_addr": parent_addr,
            "inbound_refs": inbound,
            "cross_sub_count": len(cross_sub_refs),
        })

    return results


def _sort_labels(classified):
    """Sort labels by category order, then parent sub addr, then label addr."""
    cat_idx = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}
    return sorted(classified, key=lambda r: (
        cat_idx.get(r["category"], 99),
        r["parent_sub_addr"] or 0,
        r["addr"],
    ))


def _extract_asm_window(asm_lines, addr_to_line, label_to_line, center_addr,
                        window=20):
    """Extract ±window lines around a label address."""
    target = f"0x{center_addr:04X}"
    center_line = find_line_for_target(
        target, asm_lines, addr_to_line, label_to_line)
    if center_line is None:
        return None

    start = max(0, center_line - window)
    end = min(len(asm_lines), center_line + window + 1)

    result = []
    for i in range(start, end):
        result.append(f"{i + 1:5d}  {asm_lines[i]}")
    return "".join(result)


def _extract_sub_asm(asm_lines, addr_to_line, label_to_line, sub_addr,
                     next_sub_addr):
    """Extract the full assembly listing for a subroutine."""
    start_target = f"0x{sub_addr:04X}"
    start_line = find_line_for_target(
        start_target, asm_lines, addr_to_line, label_to_line)
    if start_line is None:
        return None

    # Back up to include preceding comment/label lines
    while start_line > 0 and not re.search(
            r";\s*[0-9a-f]{4}:", asm_lines[start_line - 1]):
        stripped = asm_lines[start_line - 1].strip()
        if stripped == "" or stripped.startswith(";") or stripped.startswith("."):
            start_line -= 1
        else:
            break

    if next_sub_addr is not None:
        end_target = f"0x{next_sub_addr:04X}"
        end_line = find_line_for_target(
            end_target, asm_lines, addr_to_line, label_to_line)
        if end_line is not None:
            while end_line > start_line and asm_lines[end_line - 1].strip() == "":
                end_line -= 1
        else:
            end_line = min(start_line + 100, len(asm_lines))
    else:
        end_line = min(start_line + 100, len(asm_lines))

    result = []
    for i in range(start_line, end_line):
        result.append(f"{i + 1:5d}  {asm_lines[i]}")
    return "".join(result)


def _format_label_file(rec, order, total, asm_lines, addr_to_line,
                       label_to_line, audit_by_addr):
    """Format a single label context file."""
    out = []
    sep = "=" * 78

    # Header
    out.append(sep)
    out.append(f"LABEL: {rec['name']} (&{rec['addr']:04X})")
    out.append(sep)
    out.append(f"Category: {rec['category']}")
    if rec["parent_sub_name"]:
        out.append(
            f"Parent subroutine: {rec['parent_sub_name']}"
            f" (&{rec['parent_sub_addr']:04X})"
        )
    total_refs = len(rec["inbound_refs"])
    cross_refs = rec["cross_sub_count"]
    out.append(
        f"Inbound references: {total_refs}"
        f" ({cross_refs} cross-subroutine)"
    )
    out.append(f"Processing order: {order:03d} of {total}")
    out.append("")

    # Inbound references
    out.append("INBOUND REFERENCES")
    out.append("-" * 40)
    if rec["inbound_refs"]:
        for ref in rec["inbound_refs"]:
            cross_tag = "cross-sub" if ref["cross_sub"] else "same-sub"
            out.append(
                f"  &{ref['addr']:04X}  {ref['mnemonic']:<4s} {rec['name']}"
                f"   in {ref['sub_name']} ({cross_tag})"
            )
    else:
        out.append("  (no inbound references found)")
    out.append("")

    # Assembly context (±20 lines around label)
    out.append(f"ASSEMBLY CONTEXT (+/-20 lines around label)")
    out.append(sep)
    window_text = _extract_asm_window(
        asm_lines, addr_to_line, label_to_line, rec["addr"])
    if window_text:
        out.append(window_text.rstrip())
    else:
        out.append(f"(could not extract assembly for &{rec['addr']:04X})")
    out.append("")

    # Parent subroutine assembly
    if rec["parent_sub_addr"] is not None:
        parent = audit_by_addr.get(rec["parent_sub_addr"])
        if parent:
            next_addr = parent["next_sub"]["addr"] if parent.get("next_sub") else None
            out.append("PARENT SUBROUTINE ASSEMBLY")
            out.append(sep)
            parent_asm = _extract_sub_asm(
                asm_lines, addr_to_line, label_to_line,
                rec["parent_sub_addr"], next_addr)
            if parent_asm:
                out.append(parent_asm.rstrip())
            else:
                out.append(
                    f"(could not extract assembly for "
                    f"&{rec['parent_sub_addr']:04X})"
                )
            out.append("")

    # Rename template
    out.append("RENAME TEMPLATE")
    out.append(sep)
    out.append("# Add to disasm_nfs_360.py:")
    out.append(f'label(0x{rec["addr"]:04X}, "new_name")')

    if rec["category"] == "subroutine":
        out.append("")
        out.append("# If promoting to subroutine, also add:")
        out.append(
            f'subroutine(0x{rec["addr"]:04X}, hook=None,\n'
            f'    title="Short title",\n'
            f'    description="""\\\n'
            f'Description of what this subroutine does.""")'
        )
    out.append("")

    return "\n".join(out) + "\n"


def _write_summary_file(output_dirpath, classified, version):
    """Write 000_SUMMARY.txt listing all labels grouped by category."""
    lines = []
    lines.append(f"NFS {version} Auto-Generated Label Summary")
    lines.append("=" * 60)
    lines.append(f"Total auto-generated labels: {len(classified)}")
    lines.append("")

    # Category counts
    cat_counts = {}
    for rec in classified:
        cat_counts[rec["category"]] = cat_counts.get(rec["category"], 0) + 1
    for cat in CATEGORY_ORDER:
        count = cat_counts.get(cat, 0)
        lines.append(f"  {cat:<24s} {count:>4d}")
    lines.append("")

    # Full listing
    lines.append(
        f"{'ORDER':>5s}  {'ADDR':<7s} {'CATEGORY':<22s} "
        f"{'REFS':>4s}  {'XREF':>4s}  {'PARENT':<28s}  {'NAME'}"
    )
    lines.append(
        f"{'-----':>5s}  {'----':<7s} {'--------':<22s} "
        f"{'----':>4s}  {'----':>4s}  {'------':<28s}  {'----'}"
    )

    for idx, rec in enumerate(classified):
        addr_str = f"&{rec['addr']:04X}"
        parent = rec["parent_sub_name"] or ""
        lines.append(
            f"{idx + 1:>5d}  {addr_str:<7s} {rec['category']:<22s} "
            f"{len(rec['inbound_refs']):>4d}  {rec['cross_sub_count']:>4d}"
            f"  {parent:<28s}  {rec['name']}"
        )

    filepath = output_dirpath / "000_SUMMARY.txt"
    filepath.write_text("\n".join(lines) + "\n")


def _print_summary(classified):
    """Print summary statistics to stdout."""
    total = len(classified)
    cat_counts = {}
    for rec in classified:
        cat_counts[rec["category"]] = cat_counts.get(rec["category"], 0) + 1

    print(f"Auto-generated labels: {total}")
    for cat in CATEGORY_ORDER:
        count = cat_counts.get(cat, 0)
        print(f"  {cat:<24s} {count:>4d}")


def generate_labels(version_dirpath, version, output_dirpath=None,
                    category_filter=None, single_label=None,
                    summary_only=False):
    """Generate per-label context files.

    Returns exit code (0 success, 1 error).
    """
    from disasm_tools.paths import rom_prefix
    pfx = rom_prefix(version_dirpath)
    json_filepath = version_dirpath / "output" / f"{pfx}-{version}.json"
    asm_filepath = version_dirpath / "output" / f"{pfx}-{version}.asm"

    if not json_filepath.exists():
        print(
            f"Error: {json_filepath} not found (run disassemble first)",
            file=sys.stderr,
        )
        return 1
    if not asm_filepath.exists():
        print(
            f"Error: {asm_filepath} not found (run disassemble first)",
            file=sys.stderr,
        )
        return 1

    if output_dirpath is None:
        output_dirpath = version_dirpath / "labels"

    # Load data
    data = json.loads(json_filepath.read_text())
    items = data["items"]
    memory_regions = build_memory_regions(data.get("meta", {}))

    # Collect auto-generated labels
    auto_labels = _collect_auto_labels(items)
    if not auto_labels:
        print("No auto-generated labels found.")
        return 0

    # Build reference index
    target_refs = _build_target_refs(items)

    # Load audit subroutines for extent info
    audit_subs = load_subroutines(json_filepath)
    audit_by_addr = {s["addr"]: s for s in audit_subs}

    # Classify labels
    classified = _classify_labels(
        auto_labels, items, target_refs, audit_subs, memory_regions)

    # Sort
    classified = _sort_labels(classified)

    # Filter by category
    if category_filter:
        if category_filter not in CATEGORY_ORDER:
            print(
                f"Unknown category '{category_filter}'. "
                f"Available: {', '.join(CATEGORY_ORDER)}",
                file=sys.stderr,
            )
            return 1
        classified = [r for r in classified if r["category"] == category_filter]

    # Filter by single label
    if single_label:
        addr_str = single_label.strip().lstrip("$&").removeprefix("0x")
        try:
            target_addr = int(addr_str, 16)
        except ValueError:
            target_addr = None
        matches = [
            r for r in classified
            if r["addr"] == target_addr or single_label == r["name"]
        ]
        if not matches:
            print(f"Label '{single_label}' not found", file=sys.stderr)
            return 1
        classified = matches

    if summary_only:
        _print_summary(classified)
        return 0

    # Load ASM for context extraction
    asm_lines = asm_filepath.read_text().splitlines(keepends=True)
    addr_to_line, label_to_line = build_index(asm_lines)

    # Write files
    output_dirpath = Path(output_dirpath)
    output_dirpath.mkdir(parents=True, exist_ok=True)

    _write_summary_file(output_dirpath, classified, version)

    total = len(classified)
    for idx, rec in enumerate(classified):
        order = idx + 1
        filename = (
            f"{order:03d}_{rec['category']}_{rec['name']}"
            f"_{rec['addr']:04X}.txt"
        )
        filepath = output_dirpath / filename
        content = _format_label_file(
            rec, order, total, asm_lines, addr_to_line, label_to_line,
            audit_by_addr)
        filepath.write_text(content)

    print(f"Wrote {total} label context files to {output_dirpath}")
    return 0
