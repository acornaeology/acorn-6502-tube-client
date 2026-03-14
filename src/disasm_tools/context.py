"""Generate per-subroutine context files for inline commenting work.

Extracts each candidate subroutine into a self-contained text file with
its assembly listing, callers, callees (with their assembly), comment
density stats, and ready-to-fill comment() templates. Files are ordered
by call-graph depth (leaves first) so simpler routines are documented
before their callers.
"""

import json
import re
import sys
from pathlib import Path

import networkx as nx

from disasm_tools.audit import load_subroutines
from disasm_tools.asm_extract import build_index, find_line_for_target
from disasm_tools.cfg import build_call_graph


def _compute_depths(G):
    """Compute call-graph depth for each internal node. Depth 0 = leaf."""
    internal = {n for n in G.nodes if not G.nodes[n].get("external")}
    H = G.subgraph(internal).copy()

    if nx.is_directed_acyclic_graph(H):
        depths = {}
        for node in reversed(list(nx.topological_sort(H))):
            succs = list(H.successors(node))
            depths[node] = 1 + max(depths[s] for s in succs) if succs else 0
    else:
        condensation = nx.condensation(H)
        mapping = condensation.graph["mapping"]
        scc_depths = {}
        for scc_node in reversed(list(nx.topological_sort(condensation))):
            succs = list(condensation.successors(scc_node))
            scc_depths[scc_node] = (
                1 + max(scc_depths[s] for s in succs) if succs else 0
            )
        depths = {node: scc_depths[mapping[node]] for node in internal}

    return depths


def _extract_asm_range(lines, addr_to_line, label_to_line, start_addr,
                       end_addr=None):
    """Extract assembly lines for an address range, with context."""
    start_target = f"0x{start_addr:04X}"
    start_line = find_line_for_target(
        start_target, lines, addr_to_line, label_to_line)
    if start_line is None:
        return None

    # Back up to include preceding comment/label lines
    while start_line > 0 and not re.search(
            r";\s*[0-9a-f]{4}:", lines[start_line - 1]):
        stripped = lines[start_line - 1].strip()
        if stripped == "" or stripped.startswith(";") or stripped.startswith("."):
            start_line -= 1
        else:
            break

    if end_addr is not None:
        end_target = f"0x{end_addr:04X}"
        end_line = find_line_for_target(
            end_target, lines, addr_to_line, label_to_line)
        if end_line is not None:
            # Back up over blank lines between subs
            while end_line > start_line and lines[end_line - 1].strip() == "":
                end_line -= 1
        else:
            end_line = min(start_line + 60, len(lines))
    else:
        end_line = len(lines)

    result = []
    for i in range(start_line, end_line):
        result.append(f"{i + 1:5d}  {lines[i]}")
    return "".join(result)


def _format_on_entry_exit(sub):
    """Format on_entry and on_exit dicts as text."""
    parts = []
    if sub.get("on_entry"):
        parts.append("On Entry:")
        oe = sub["on_entry"]
        if isinstance(oe, dict):
            for reg, desc in oe.items():
                parts.append(f"    {reg}: {desc}")
        else:
            parts.append(f"    {oe}")
    if sub.get("on_exit"):
        parts.append("On Exit:")
        ox = sub["on_exit"]
        if isinstance(ox, dict):
            for reg, desc in ox.items():
                parts.append(f"    {reg}: {desc}")
        else:
            parts.append(f"    {ox}")
    return "\n".join(parts)


def generate_context(version_dirpath, version, threshold=50,
                     output_dirpath=None, single_sub=None, summary_only=False):
    """Generate per-subroutine context files.

    Returns exit code (0 success, 1 error).
    """
    from disasm_tools.paths import rom_prefix
    pfx = rom_prefix(version_dirpath)
    json_filepath = version_dirpath / "output" / f"{pfx}-{version}.json"
    asm_filepath = version_dirpath / "output" / f"{pfx}-{version}.asm"

    if not json_filepath.exists():
        print(f"Error: {json_filepath} not found (run disassemble first)",
              file=sys.stderr)
        return 1
    if not asm_filepath.exists():
        print(f"Error: {asm_filepath} not found (run disassemble first)",
              file=sys.stderr)
        return 1

    if output_dirpath is None:
        output_dirpath = version_dirpath / "context"

    # Load data
    data = json.loads(json_filepath.read_text())
    items = data["items"]
    raw_json_subs = {s["addr"]: s for s in data.get("subroutines", [])}

    # Load audit subroutines (extents, items, flags)
    audit_subs = load_subroutines(json_filepath)
    audit_by_addr = {s["addr"]: s for s in audit_subs}

    # Load ASM
    asm_lines = asm_filepath.read_text().splitlines(keepends=True)
    addr_to_line, label_to_line = build_index(asm_lines)

    # Build call graph and compute depths
    G = build_call_graph(json_filepath)
    depths = _compute_depths(G)

    # Compute inline comment density per subroutine
    sub_records = []
    for asub in audit_subs:
        addr = asub["addr"]
        node_id = f"0x{addr:04X}"

        # Count code items and inline comments
        code_items = [i for i in asub["items"] if i.get("type") == "code"]
        code_count = len(code_items)
        commented_count = sum(
            1 for i in code_items if i.get("comment_inline"))

        if code_count == 0:
            continue  # Skip pure-data subroutines

        density_pct = commented_count / code_count * 100

        # Callers and callees from graph
        callers = []
        if G.has_node(node_id):
            for pred in sorted(G.predecessors(node_id)):
                edge = G.edges[pred, node_id]
                callers.append({
                    "node_id": pred,
                    "name": G.nodes[pred].get("name", pred),
                    "call_sites": edge.get("call_sites", []),
                    "type": edge.get("type", "jsr"),
                    "external": G.nodes[pred].get("external", False),
                })

        callees = []
        if G.has_node(node_id):
            for succ in sorted(G.successors(node_id)):
                edge = G.edges[node_id, succ]
                callees.append({
                    "node_id": succ,
                    "name": G.nodes[succ].get("name", succ),
                    "title": G.nodes[succ].get("title", ""),
                    "call_sites": edge.get("call_sites", []),
                    "type": edge.get("type", "jsr"),
                    "external": G.nodes[succ].get("external", False),
                })

        # Get JSON subroutine metadata for on_entry/on_exit
        json_sub = raw_json_subs.get(addr, {})

        sub_records.append({
            "addr": addr,
            "name": asub["name"],
            "title": asub.get("title", ""),
            "description": asub.get("description", ""),
            "on_entry": json_sub.get("on_entry", ""),
            "on_exit": json_sub.get("on_exit", ""),
            "code_count": code_count,
            "commented_count": commented_count,
            "density_pct": density_pct,
            "depth": depths.get(node_id, 0),
            "callers": callers,
            "callees": callees,
            "items": asub["items"],
            "next_sub": asub.get("next_sub"),
            "flags": asub.get("flags", set()),
        })

    # Filter by single sub if requested
    if single_sub:
        addr_str = single_sub.strip().lstrip("$&").removeprefix("0x")
        try:
            target_addr = int(addr_str, 16)
        except ValueError:
            target_addr = None
        matches = [
            r for r in sub_records
            if r["addr"] == target_addr or single_sub in r["name"]
        ]
        if not matches:
            print(f"Subroutine '{single_sub}' not found", file=sys.stderr)
            return 1
        if len(matches) > 1:
            print(f"Ambiguous '{single_sub}':", file=sys.stderr)
            for m in matches:
                print(f"  &{m['addr']:04X} {m['name']}", file=sys.stderr)
            return 1
        sub_records = matches
        # Don't apply threshold filter for single sub
        candidates = sub_records
    else:
        # Filter by threshold
        candidates = [r for r in sub_records if r["density_pct"] < threshold]

    # Sort: depth ascending (leaves first), then address
    candidates.sort(key=lambda r: (r["depth"], r["addr"]))

    # Summary mode
    if summary_only:
        _print_summary(sub_records, candidates, threshold)
        return 0

    # Write context files
    output_dirpath = Path(output_dirpath)
    output_dirpath.mkdir(parents=True, exist_ok=True)

    # Write summary index
    _write_summary_file(output_dirpath, sub_records, candidates, threshold,
                        version)

    # Write per-subroutine context files
    total = len(candidates)
    for idx, rec in enumerate(candidates):
        filename = (f"{idx + 1:03d}_{rec['name']}"
                    f"_{rec['addr']:04X}.txt")
        filepath = output_dirpath / filename
        content = _format_context_file(
            rec, idx + 1, total, asm_lines, addr_to_line, label_to_line,
            audit_by_addr)
        filepath.write_text(content)

    print(f"Wrote {total} context files to {output_dirpath}")
    return 0


def _print_summary(all_subs, candidates, threshold):
    """Print summary statistics to stdout."""
    total_code = sum(r["code_count"] for r in all_subs)
    total_commented = sum(r["commented_count"] for r in all_subs)
    overall_pct = total_commented / total_code * 100 if total_code else 0

    print(f"Overall inline comment coverage: "
          f"{total_commented}/{total_code} code items ({overall_pct:.1f}%)")
    print(f"Subroutines with code: {len(all_subs)}")
    print(f"Candidates below {threshold}% threshold: {len(candidates)}")
    print()

    print(f"{'ORDER':>5s}  {'ADDR':<7s} {'DENSITY':>7s} {'DEPTH':>5s} "
          f"{'CODE':>4s}  {'NAME':<32s}")
    print(f"{'-----':>5s}  {'----':<7s} {'-------':>7s} {'-----':>5s} "
          f"{'----':>4s}  {'----':<32s}")

    for idx, rec in enumerate(candidates):
        addr_str = f"&{rec['addr']:04X}"
        density = f"{rec['density_pct']:.0f}%"
        print(f"{idx + 1:>5d}  {addr_str:<7s} {density:>7s} {rec['depth']:>5d} "
              f"{rec['code_count']:>4d}  {rec['name']:<32s}")


def _write_summary_file(output_dirpath, all_subs, candidates, threshold,
                        version):
    """Write 000_SUMMARY.txt index file."""
    total_code = sum(r["code_count"] for r in all_subs)
    total_commented = sum(r["commented_count"] for r in all_subs)
    overall_pct = total_commented / total_code * 100 if total_code else 0

    lines = []
    lines.append(f"NFS {version} Inline Comment Coverage")
    lines.append("=" * 50)
    lines.append(f"Threshold: <{threshold}%")
    lines.append(f"Candidates: {len(candidates)} of {len(all_subs)} "
                 f"subroutines (with code)")
    lines.append(f"Overall coverage: {total_commented}/{total_code} "
                 f"code items ({overall_pct:.1f}%)")
    lines.append("")
    lines.append(f"{'ORDER':>5s}  {'ADDR':<7s} {'DENSITY':>7s} {'DEPTH':>5s} "
                 f"{'CODE':>4s}  {'NAME'}")
    lines.append(f"{'-----':>5s}  {'----':<7s} {'-------':>7s} {'-----':>5s} "
                 f"{'----':>4s}  {'----'}")

    for idx, rec in enumerate(candidates):
        addr_str = f"&{rec['addr']:04X}"
        density = f"{rec['density_pct']:.0f}%"
        lines.append(
            f"{idx + 1:>5d}  {addr_str:<7s} {density:>7s} {rec['depth']:>5d} "
            f"{rec['code_count']:>4d}  {rec['name']}")

    filepath = output_dirpath / "000_SUMMARY.txt"
    filepath.write_text("\n".join(lines) + "\n")


def _format_context_file(rec, order, total, asm_lines, addr_to_line,
                         label_to_line, audit_by_addr):
    """Format a single subroutine context file."""
    out = []
    sep = "=" * 78

    # Header
    out.append(sep)
    out.append(f"SUBROUTINE: {rec['name']} (&{rec['addr']:04X})")
    out.append(sep)
    if rec["title"]:
        out.append(f"Title: {rec['title']}")
    depth_label = "leaf" if rec["depth"] == 0 else f"depth {rec['depth']}"
    out.append(f"Depth: {rec['depth']} ({depth_label})")
    out.append(f"Comment density: {rec['commented_count']}/{rec['code_count']}"
               f" code items ({rec['density_pct']:.0f}%)")
    out.append(f"Processing order: {order:03d} of {total}")
    if rec["flags"]:
        out.append(f"Flags: {', '.join(sorted(rec['flags']))}")
    out.append("")

    # Description
    if rec["description"] or rec["title"]:
        out.append("DESCRIPTION")
        out.append("-" * 40)
        if rec["description"]:
            out.append(rec["description"])
        elif rec["title"]:
            out.append(f"(title only: {rec['title']})")
        out.append("")

    # On entry/exit
    entry_exit = _format_on_entry_exit(rec)
    if entry_exit:
        out.append(entry_exit)
        out.append("")

    # Callers
    out.append(f"CALLERS ({len(rec['callers'])})")
    out.append("-" * 40)
    if rec["callers"]:
        for caller in rec["callers"]:
            sites = ", ".join(caller["call_sites"])
            type_suffix = f" [{caller['type'].upper()}]" if caller["type"] != "jsr" else ""
            out.append(f"  {caller['node_id']} {caller['name']}"
                       f"  at {sites}{type_suffix}")
    else:
        out.append("  (no callers)")
    out.append("")

    # Callees
    out.append(f"CALLEES ({len(rec['callees'])})")
    out.append("-" * 40)
    if rec["callees"]:
        for callee in rec["callees"]:
            sites = ", ".join(callee["call_sites"])
            ext = " [external]" if callee["external"] else ""
            type_suffix = f" [{callee['type'].upper()}]" if callee["type"] != "jsr" else ""
            title = f"  -- {callee['title']}" if callee["title"] else ""
            out.append(f"  {callee['node_id']} {callee['name']}"
                       f"  at {sites}{type_suffix}{ext}{title}")
    else:
        out.append("  (leaf subroutine -- no calls)")
    out.append("")

    # Assembly listing
    out.append(sep)
    out.append("ASSEMBLY LISTING")
    out.append(sep)
    end_addr = rec["next_sub"]["addr"] if rec["next_sub"] else None
    asm_text = _extract_asm_range(
        asm_lines, addr_to_line, label_to_line, rec["addr"], end_addr)
    if asm_text:
        out.append(asm_text.rstrip())
    else:
        out.append(f"(could not extract assembly for &{rec['addr']:04X})")
    out.append("")

    # Callee assembly
    internal_callees = [c for c in rec["callees"] if not c["external"]]
    if internal_callees:
        out.append(sep)
        out.append("CALLEE ASSEMBLY")
        out.append(sep)
        for callee in internal_callees:
            callee_addr = int(callee["node_id"].removeprefix("0x"), 16)
            callee_sub = audit_by_addr.get(callee_addr)
            out.append("")
            out.append(f"--- {callee['name']} ({callee['node_id']}) ---")
            if callee["title"]:
                out.append(f"Title: {callee['title']}")
            # Get description from audit data
            if callee_sub and callee_sub.get("description"):
                out.append(f"Description: {callee_sub['description']}")
            out.append("")

            callee_end = None
            if callee_sub and callee_sub.get("next_sub"):
                callee_end = callee_sub["next_sub"]["addr"]
            callee_asm = _extract_asm_range(
                asm_lines, addr_to_line, label_to_line,
                callee_addr, callee_end)
            if callee_asm:
                out.append(callee_asm.rstrip())
            else:
                out.append(f"(could not extract assembly)")
        out.append("")
    elif rec["callees"]:
        # Only external callees
        out.append(sep)
        out.append("CALLEE ASSEMBLY")
        out.append(sep)
        out.append("(all callees are external OS entry points)")
        out.append("")

    # Comment templates
    uncommented = []
    for item in rec["items"]:
        if item.get("type") != "code":
            continue
        if item.get("comment_inline"):
            continue
        mnemonic = item.get("mnemonic", "?")
        operand = item.get("operand", "")
        hint = f"{mnemonic} {operand}".strip()
        uncommented.append((item["addr"], hint))

    if uncommented:
        out.append(sep)
        out.append("COMMENT TEMPLATES")
        out.append(sep)
        out.append("# Uncommented code addresses — fill in and add to driver:")
        for addr, hint in uncommented:
            out.append(f'comment(0x{addr:04X}, "", inline=True)'
                       f"    # {hint}")
        out.append("")

    return "\n".join(out) + "\n"
