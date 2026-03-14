"""Audit subroutine annotations in NFS ROM disassembly output.

Analyses the JSON output to compute subroutine extents, detect fall-throughs,
find entry references, and flag potential annotation issues. Output modes:
  --summary:      Table of all subroutines with computed flags
  --sub <target>: Full audit report for one subroutine (declared or undeclared)
  --flag <FLAG>:  Summary filtered to one flag category
  --undeclared:   List JSR targets without subroutine() declarations
"""

import json
import re
import sys
from pathlib import Path

# Mnemonics that unconditionally terminate control flow
TERMINATING_MNEMONICS = {"rts", "jmp", "brk", "rti"}

# Branch mnemonics (conditional)
BRANCH_MNEMONICS = {"bcc", "bcs", "beq", "bne", "bmi", "bpl", "bvc", "bvs"}

# Memory regions: subroutines only extend within their region.
# The ROM region is added dynamically by build_memory_regions() based on JSON metadata.
BASE_MEMORY_REGIONS = [
    (0x0016, 0x0076),   # zero page workspace
    (0x0400, 0x04FF),   # relocated page 4
    (0x0500, 0x05FF),   # relocated page 5
    (0x0600, 0x06FF),   # relocated page 6
    (0x0D00, 0x0DFF),   # NMI workspace
]


def build_memory_regions(meta):
    """Build MEMORY_REGIONS list with ROM range from JSON metadata."""
    load_addr = meta["load_addr"]
    end_addr = meta["end_addr"] - 1
    return BASE_MEMORY_REGIONS + [(load_addr, end_addr)]


def region_for_addr(addr, memory_regions):
    """Return the memory region (start, end) containing addr, or None."""
    for start, end in memory_regions:
        if start <= addr <= end:
            return (start, end)
    return None


def find_containing_sub(addr, rom_subs):
    """Find the subroutine containing addr (last sub with start <= addr)."""
    result = None
    for s in rom_subs:
        if s["addr"] <= addr:
            result = s
        else:
            break
    return result


def scan_routine_range(addr, items_by_addr, sorted_addrs):
    """Scan forward from addr to find the routine's terminating instruction.

    Returns (range_end, code_count, data_count, falls_through).
    range_end is the address of the terminating instruction, or None if
    the routine falls through without terminating.
    """
    try:
        addr_idx = sorted_addrs.index(addr)
    except ValueError:
        return None, 0, 0, True

    code_count = 0
    data_count = 0

    for i in range(addr_idx, len(sorted_addrs)):
        a = sorted_addrs[i]
        scan_item = items_by_addr[a]
        if scan_item.get("type") == "code":
            code_count += 1
        else:
            data_count += 1
        if scan_item.get("mnemonic") in TERMINATING_MNEMONICS:
            return a, code_count, data_count, False

    return None, code_count, data_count, True


def load_subroutines(json_filepath):
    """Load JSON output, compute subroutine extents and flags.

    Returns a list of subroutine dicts augmented with:
      items, code_count, data_count, last_mnemonic, terminates,
      next_sub, entry_refs, escaping_branches, flags
    """
    data = json.loads(Path(json_filepath).read_text())
    items = data["items"]
    raw_subs = data.get("subroutines", [])
    memory_regions = build_memory_regions(data.get("meta", {}))

    # Filter out OS entry points (addr >= 0xFF00) — these are stubs
    rom_subs = [s for s in raw_subs if s["addr"] < 0xFF00]
    rom_subs.sort(key=lambda s: s["addr"])

    # Build addr→item index
    items_by_addr = {item["addr"]: item for item in items}
    sorted_items = sorted(items, key=lambda i: i["addr"])

    # Build target→referencing-items index for entry ref lookups
    target_refs = {}
    for item in items:
        t = item.get("target")
        if t is not None:
            target_refs.setdefault(t, []).append(item)

    # First pass: compute extents and basic properties for all subs,
    # so the second pass can look up predecessor termination status.
    sub_data = []

    for idx, sub in enumerate(rom_subs):
        sub_addr = sub["addr"]
        sub_region = region_for_addr(sub_addr, memory_regions)

        # Find extent end: next sub in same region, or region end
        extent_end = None
        next_sub_info = None
        for j in range(idx + 1, len(rom_subs)):
            candidate = rom_subs[j]
            if region_for_addr(candidate["addr"], memory_regions) == sub_region:
                extent_end = candidate["addr"]
                next_sub_info = {
                    "addr": candidate["addr"],
                    "name": candidate.get("name", "?"),
                }
                break

        # Collect items in this sub's extent
        sub_items = []
        for item in sorted_items:
            if item["addr"] < sub_addr:
                continue
            if extent_end is not None and item["addr"] >= extent_end:
                break
            # Must be in same region
            if sub_region and region_for_addr(item["addr"], memory_regions) == sub_region:
                sub_items.append(item)
            elif sub_region is None:
                if extent_end is None or item["addr"] < extent_end:
                    sub_items.append(item)

        code_count = sum(1 for i in sub_items if i.get("type") == "code")
        data_count = len(sub_items) - code_count

        # Find last code item for termination check
        code_items = [i for i in sub_items if i.get("type") == "code"]
        last_mnemonic = code_items[-1].get("mnemonic") if code_items else None
        terminates = last_mnemonic in TERMINATING_MNEMONICS if last_mnemonic else False

        # py8dis reference tracking: the 'references' field on the item at
        # sub_addr lists all addresses that reference this location, including
        # operand targets, data table entries, and relocated code pointers.
        item_at_addr = items_by_addr.get(sub_addr)
        has_any_refs = bool(item_at_addr and item_at_addr.get("references"))

        # Entry references: JSR/JMP from elsewhere targeting this sub's addr
        entry_refs = []
        for ref_item in target_refs.get(sub_addr, []):
            if ref_item.get("mnemonic") in ("jsr", "jmp"):
                containing = find_containing_sub(ref_item["addr"], rom_subs)
                ref_sub_name = containing.get("name", f"&{containing['addr']:04X}") if containing else "?"
                entry_refs.append({
                    "addr": ref_item["addr"],
                    "mnemonic": ref_item["mnemonic"],
                    "in_sub": ref_sub_name,
                })

        # Branch references (conditional branches targeting this sub's addr)
        branch_entry_refs = []
        for ref_item in target_refs.get(sub_addr, []):
            if ref_item.get("mnemonic") in BRANCH_MNEMONICS:
                containing = find_containing_sub(ref_item["addr"], rom_subs)
                ref_sub_name = containing.get("name", f"&{containing['addr']:04X}") if containing else "?"
                branch_entry_refs.append({
                    "addr": ref_item["addr"],
                    "mnemonic": ref_item["mnemonic"],
                    "in_sub": ref_sub_name,
                })

        # Escaping branches: branch items within extent whose target is outside
        escaping_branches = []
        for item in sub_items:
            if item.get("mnemonic") in BRANCH_MNEMONICS:
                target = item.get("target")
                if target is not None:
                    in_extent = (sub_addr <= target < extent_end) if extent_end else (target >= sub_addr)
                    if not in_extent:
                        escaping_branches.append({
                            "addr": item["addr"],
                            "mnemonic": item["mnemonic"],
                            "target": target,
                            "target_label": item.get("target_label", f"&{target:04X}"),
                        })

        sub_data.append({
            "sub": sub,
            "idx": idx,
            "sub_addr": sub_addr,
            "sub_region": sub_region,
            "sub_items": sub_items,
            "code_count": code_count,
            "data_count": data_count,
            "last_mnemonic": last_mnemonic,
            "terminates": terminates,
            "next_sub_info": next_sub_info,
            "has_any_refs": has_any_refs,
            "entry_refs": entry_refs,
            "branch_entry_refs": branch_entry_refs,
            "escaping_branches": escaping_branches,
        })

    # Second pass: compute flags using predecessor termination info
    results = []
    for i, sd in enumerate(sub_data):
        sub = sd["sub"]
        flags = set()

        if not sd["terminates"] and sd["next_sub_info"]:
            flags.add("FALL_THROUGH")

        # Determine predecessor in same region
        prev_terminates = True  # default for first sub in region
        if i > 0 and sub_data[i - 1]["sub_region"] == sd["sub_region"]:
            prev_terminates = sub_data[i - 1]["terminates"]

        has_direct_refs = bool(sd["entry_refs"]) or bool(sd["branch_entry_refs"])

        if not has_direct_refs and not sd["has_any_refs"]:
            if not prev_terminates:
                # Predecessor falls through AND no references anywhere —
                # genuinely reached only via fall-through
                flags.add("FALL_THROUGH_ENTRY")
            else:
                # Predecessor terminates but no references found —
                # likely called indirectly (dispatch table, vector, NMI install)
                flags.add("NO_REFS")
        elif not has_direct_refs and sd["has_any_refs"]:
            # Referenced somewhere (e.g. address taken for a table or vector)
            # but not via direct JSR/JMP/branch
            if not prev_terminates:
                flags.add("FALL_THROUGH_ENTRY")

        if sd["escaping_branches"]:
            flags.add("BRANCH_ESCAPE")

        if sd["code_count"] == 0 and sd["data_count"] > 0:
            flags.add("DATA_ONLY")

        name = sub.get("name", "")
        if re.match(r"sub_c[0-9a-f]+$", name):
            flags.add("AUTO_NAME")

        title = sub.get("title", "")
        description = sub.get("description", "")
        if not title and not description:
            flags.add("NO_DESCRIPTION")
        elif len(title) + len(description) < 40 and not description:
            flags.add("NO_DESCRIPTION")

        results.append({
            "addr": sd["sub_addr"],
            "name": name or f"&{sd['sub_addr']:04X}",
            "title": title,
            "description": description,
            "on_entry": sub.get("on_entry", ""),
            "on_exit": sub.get("on_exit", ""),
            "items": sd["sub_items"],
            "code_count": sd["code_count"],
            "data_count": sd["data_count"],
            "last_mnemonic": sd["last_mnemonic"],
            "terminates": sd["terminates"],
            "next_sub": sd["next_sub_info"],
            "entry_refs": sd["entry_refs"],
            "branch_entry_refs": sd["branch_entry_refs"],
            "escaping_branches": sd["escaping_branches"],
            "flags": flags,
        })

    return results


def end_type(sub):
    """Short string describing how a subroutine ends."""
    if sub["terminates"]:
        m = sub["last_mnemonic"].upper()
        return m
    if sub["next_sub"]:
        return "FALL\u2192"
    return "END"


def format_summary(subs, flag_filter=None):
    """Print summary table to stdout."""
    if flag_filter:
        flag_upper = flag_filter.upper()
        subs = [s for s in subs if flag_upper in s["flags"]]

    if not subs:
        print("No subroutines match the filter.")
        return

    # Header
    print(f"{'ADDR':<7s} {'NAME':<32s} {'END':<7s} {'ITEMS':>7s}  FLAGS")
    print(f"{'----':<7s} {'----':<32s} {'---':<7s} {'-----':>7s}  -----")

    for sub in subs:
        addr_str = f"&{sub['addr']:04X}"
        name = sub["name"][:31]
        end = end_type(sub)
        items_str = f"{sub['code_count']}/{sub['data_count']}"
        flags_str = ",".join(sorted(sub["flags"])) if sub["flags"] else ""
        print(f"{addr_str:<7s} {name:<32s} {end:<7s} {items_str:>7s}  {flags_str}")

    # Summary counts
    total = len(subs)
    rts_count = sum(1 for s in subs if s["last_mnemonic"] == "rts")
    jmp_count = sum(1 for s in subs if s["last_mnemonic"] == "jmp")
    fall_count = sum(1 for s in subs if not s["terminates"])
    print(f"\n{total} subroutines: {rts_count} RTS, {jmp_count} JMP, {fall_count} fall-through")

    # Flag totals
    all_flags = set()
    for s in subs:
        all_flags.update(s["flags"])
    if all_flags:
        flag_counts = []
        for flag in sorted(all_flags):
            count = sum(1 for s in subs if flag in s["flags"])
            flag_counts.append(f"{count} {flag}")
        print(f"Flags: {', '.join(flag_counts)}")


def format_detail(sub, asm_filepath):
    """Print full audit report for one subroutine."""
    print(f"## {sub['name']} (&{sub['addr']:04X})")

    if sub["title"]:
        print(f"Title: {sub['title']}")

    flags_str = ", ".join(sorted(sub["flags"])) if sub["flags"] else "none"
    print(f"Flags: {flags_str}")

    # Description
    print(f"\n### Description")
    if sub["description"]:
        print(sub["description"])
    elif sub["title"]:
        print(f"(title only: {sub['title']})")
    else:
        print("(no description)")

    if sub["on_entry"]:
        print(f"\nOn entry: {sub['on_entry']}")
    if sub["on_exit"]:
        print(f"On exit: {sub['on_exit']}")

    # Extent
    print(f"\n### Extent")
    if sub["items"]:
        first_addr = sub["items"][0]["addr"]
        last_addr = sub["items"][-1]["addr"]
        print(f"Address range: &{first_addr:04X}-&{last_addr:04X} "
              f"({sub['code_count']} code, {sub['data_count']} data items)")
    else:
        print("(no items)")

    end = end_type(sub)
    if sub["terminates"]:
        last_code = None
        for item in reversed(sub["items"]):
            if item.get("type") == "code":
                last_code = item
                break
        if last_code:
            operand = last_code.get("operand", "")
            print(f"Ends: {last_code['mnemonic'].upper()} {operand} (&{last_code['addr']:04X})")
    elif sub["next_sub"]:
        ns = sub["next_sub"]
        print(f"Ends: FALLS THROUGH to {ns['name']} (&{ns['addr']:04X})")

    # Called by
    all_refs = sub["entry_refs"]
    if all_refs:
        print(f"\n### Called by ({len(all_refs)} references)")
        for ref in sorted(all_refs, key=lambda r: r["addr"]):
            print(f"  &{ref['addr']:04X} {ref['mnemonic'].upper():<4s} "
                  f"(in {ref['in_sub']})")
    else:
        print(f"\n### Called by (0 references)")

    # Branch entry refs
    if sub["branch_entry_refs"]:
        print(f"\n### Branch entries ({len(sub['branch_entry_refs'])} references)")
        for ref in sorted(sub["branch_entry_refs"], key=lambda r: r["addr"]):
            print(f"  &{ref['addr']:04X} {ref['mnemonic'].upper():<4s} "
                  f"(in {ref['in_sub']})")

    # Escaping branches
    if sub["escaping_branches"]:
        print(f"\n### Escaping branches")
        for br in sorted(sub["escaping_branches"], key=lambda b: b["addr"]):
            print(f"  &{br['addr']:04X} {br['mnemonic'].upper()} "
                  f"\u2192 &{br['target']:04X} {br['target_label']}")

    # Assembly listing
    if asm_filepath and Path(asm_filepath).exists():
        from disasm_tools.asm_extract import build_index, find_line_for_target

        lines = Path(asm_filepath).read_text().splitlines(keepends=True)
        addr_to_line, label_to_line = build_index(lines)

        start_target = f"0x{sub['addr']:04X}"
        start_line = find_line_for_target(start_target, lines, addr_to_line, label_to_line)

        if start_line is not None:
            # Back up to include preceding comment/label lines
            while start_line > 0 and not re.search(r";\s*[0-9a-f]{4}:", lines[start_line - 1]):
                stripped = lines[start_line - 1].strip()
                if stripped == "" or stripped.startswith(";") or stripped.startswith("."):
                    start_line -= 1
                else:
                    break

            # Find end: use next_sub addr or fixed window
            if sub["next_sub"]:
                end_target = f"0x{sub['next_sub']['addr']:04X}"
                end_line = find_line_for_target(end_target, lines, addr_to_line, label_to_line)
                if end_line is not None:
                    # Back up over blank lines between subs
                    while end_line > start_line and lines[end_line - 1].strip() == "":
                        end_line -= 1
                else:
                    end_line = min(start_line + 60, len(lines))
            else:
                # Last sub in region — use last item addr
                if sub["items"]:
                    last_target = f"0x{sub['items'][-1]['addr']:04X}"
                    end_line = find_line_for_target(last_target, lines, addr_to_line, label_to_line)
                    if end_line is not None:
                        end_line += 1
                    else:
                        end_line = min(start_line + 60, len(lines))
                else:
                    end_line = min(start_line + 20, len(lines))

            print(f"\n### Assembly")
            for i in range(start_line, end_line):
                print(f"{i+1:5d}  {lines[i]}", end="")
            if not lines[end_line - 1].endswith("\n"):
                print()


def find_sub(subs, target, quiet=False):
    """Find a subroutine by address (hex) or name."""
    # Try as hex address
    addr_str = target.strip().lstrip("$&").removeprefix("0x")
    try:
        addr = int(addr_str, 16)
        for s in subs:
            if s["addr"] == addr:
                return s
    except ValueError:
        pass

    # Try as exact name
    for s in subs:
        if s["name"] == target:
            return s

    # Try partial name match
    matches = [s for s in subs if target in s["name"]]
    if len(matches) == 1:
        return matches[0]
    if matches:
        print(f"Ambiguous name '{target}', matches:", file=sys.stderr)
        for m in matches:
            print(f"  &{m['addr']:04X} {m['name']}", file=sys.stderr)
        return None

    if not quiet:
        print(f"Subroutine '{target}' not found", file=sys.stderr)
    return None


ALL_FLAGS = [
    "FALL_THROUGH", "FALL_THROUGH_ENTRY", "NO_REFS", "BRANCH_ESCAPE",
    "DATA_ONLY", "AUTO_NAME", "NO_DESCRIPTION",
]


def find_undeclared_subs(json_filepath):
    """Find JSR targets that lack subroutine() declarations.

    Returns a list of dicts with: addr, name, range_start, range_end,
    range_str, code_count, data_count, caller_count, container.
    """
    data = json.loads(Path(json_filepath).read_text())
    items = data["items"]
    raw_subs = data.get("subroutines", [])

    declared_addrs = {s["addr"] for s in raw_subs}
    rom_subs = sorted(
        [s for s in raw_subs if s["addr"] < 0xFF00],
        key=lambda s: s["addr"],
    )

    items_by_addr = {item["addr"]: item for item in items}
    sorted_addrs = sorted(items_by_addr.keys())

    # Collect all JSR targets and their caller counts
    jsr_caller_counts = {}
    for item in items:
        if item.get("mnemonic") == "jsr":
            t = item["target"]
            jsr_caller_counts[t] = jsr_caller_counts.get(t, 0) + 1

    # Undeclared = JSR targets not in the declared set, with a corresponding item
    undeclared_addrs = sorted(
        t for t in jsr_caller_counts
        if t not in declared_addrs and t in items_by_addr
    )

    results = []
    for addr in undeclared_addrs:
        item = items_by_addr[addr]
        labels = item.get("labels", [])
        name = labels[0] if labels else f"&{addr:04X}"

        range_start = addr
        range_end, code_count, data_count, falls_through = \
            scan_routine_range(addr, items_by_addr, sorted_addrs)

        if falls_through:
            range_str = f"&{range_start:04X}-FALL\u2192"
        elif range_end is not None:
            range_str = f"&{range_start:04X}-&{range_end:04X}"
        else:
            range_str = f"&{range_start:04X}-?"

        container = find_containing_sub(addr, rom_subs)
        container_name = (
            container.get("name", f"&{container['addr']:04X}")
            if container else "?"
        )

        results.append({
            "addr": addr,
            "name": name,
            "range_str": range_str,
            "code_count": code_count,
            "data_count": data_count,
            "caller_count": jsr_caller_counts[addr],
            "container": container_name,
        })

    return results


def format_undeclared_summary(candidates):
    """Print summary table of undeclared subroutine candidates."""
    if not candidates:
        print("No undeclared subroutine candidates found.")
        return

    print(f"{'ADDR':<7s} {'NAME':<33s} {'RANGE':<17s} {'ITEMS':>7s} "
          f"{'CALLS':>5s}  CONTAINER")
    print(f"{'----':<7s} {'----':<33s} {'-----':<17s} {'-----':>7s} "
          f"{'-----':>5s}  ---------")

    for c in candidates:
        addr_str = f"&{c['addr']:04X}"
        name = c["name"][:32]
        items_str = f"{c['code_count']}/{c['data_count']}"
        print(f"{addr_str:<7s} {name:<33s} {c['range_str']:<17s} "
              f"{items_str:>7s} {c['caller_count']:>5d}  {c['container']}")

    total_callers = sum(c["caller_count"] for c in candidates)
    print(f"\n{len(candidates)} undeclared routines ({total_callers} JSR callers total)")


def _parse_addr(target):
    """Parse a target string as a hex address. Returns int or None."""
    addr_str = target.strip().lstrip("$&").removeprefix("0x")
    try:
        return int(addr_str, 16)
    except ValueError:
        return None


def format_undeclared_detail(target, json_filepath, asm_filepath):
    """Print detailed context report for an undeclared JSR target.

    Returns 0 on success, 1 if the address is not a valid undeclared target.
    """
    from disasm_tools.asm_extract import build_index, find_line_for_target

    addr = _parse_addr(target)
    if addr is None:
        print(f"Error: '{target}' is not a valid hex address", file=sys.stderr)
        return 1

    data = json.loads(Path(json_filepath).read_text())
    items = data["items"]
    raw_subs = data.get("subroutines", [])
    declared_addrs = {s["addr"] for s in raw_subs}

    items_by_addr = {item["addr"]: item for item in items}
    sorted_addrs = sorted(items_by_addr.keys())

    # Validate: must be a JSR target and not already declared
    jsr_targets = set()
    for item in items:
        if item.get("mnemonic") == "jsr":
            jsr_targets.add(item["target"])

    if addr in declared_addrs:
        print(f"Error: &{addr:04X} is already a declared subroutine",
              file=sys.stderr)
        return 1
    if addr not in jsr_targets:
        print(f"Error: &{addr:04X} is not a JSR target", file=sys.stderr)
        return 1
    if addr not in items_by_addr:
        print(f"Error: &{addr:04X} has no corresponding item in output",
              file=sys.stderr)
        return 1

    item = items_by_addr[addr]
    labels = item.get("labels", [])
    name = labels[0] if labels else f"&{addr:04X}"

    # Routine range
    range_end, code_count, data_count, falls_through = \
        scan_routine_range(addr, items_by_addr, sorted_addrs)

    # Container
    rom_subs = sorted(
        [s for s in raw_subs if s["addr"] < 0xFF00],
        key=lambda s: s["addr"],
    )
    container = find_containing_sub(addr, rom_subs)

    # Callers
    callers = []
    for it in items:
        if it.get("mnemonic") == "jsr" and it.get("target") == addr:
            c = find_containing_sub(it["addr"], rom_subs)
            c_name = c.get("name", f"&{c['addr']:04X}") if c else "?"
            callers.append({"addr": it["addr"], "mnemonic": "jsr",
                            "in_sub": c_name})
    # Branch callers
    for it in items:
        if it.get("mnemonic") in BRANCH_MNEMONICS and it.get("target") == addr:
            c = find_containing_sub(it["addr"], rom_subs)
            c_name = c.get("name", f"&{c['addr']:04X}") if c else "?"
            callers.append({"addr": it["addr"], "mnemonic": it["mnemonic"],
                            "in_sub": c_name})

    # Callees: JSR/JMP within the routine's range
    end_scan = range_end if range_end is not None else sorted_addrs[-1]
    callees = []
    for a in sorted_addrs:
        if a < addr:
            continue
        if a > end_scan:
            break
        it = items_by_addr[a]
        if it.get("mnemonic") in ("jsr", "jmp"):
            t = it.get("target")
            t_label = it.get("target_label", f"&{t:04X}" if t else "?")
            # Mark as external if target >= 0xFF00
            external = t is not None and t >= 0xFF00
            callees.append({"addr": a, "mnemonic": it["mnemonic"],
                            "target": t, "target_label": t_label,
                            "external": external})

    # Collect inline comments from items in range
    inline_comments = []
    for a in sorted_addrs:
        if a < addr:
            continue
        if a > end_scan:
            break
        it = items_by_addr[a]
        comment = it.get("comment_inline")
        if comment:
            # Take first line only for summary
            first_line = comment.split("\n")[0]
            inline_comments.append((a, first_line))

    # Print report
    print(f"## {name} (&{addr:04X}) [UNDECLARED]")
    if container:
        c_name = container.get("name", f"&{container['addr']:04X}")
        print(f"Container: {c_name} (&{container['addr']:04X})")

    # Extent
    print(f"\n### Extent")
    if range_end is not None:
        print(f"Address range: &{addr:04X}-&{range_end:04X} "
              f"({code_count} code, {data_count} data items)")
        term_item = items_by_addr[range_end]
        operand = term_item.get("operand", "")
        print(f"Ends: {term_item['mnemonic'].upper()} {operand}")
    elif falls_through:
        print(f"Address range: &{addr:04X}-FALL\u2192 "
              f"({code_count} code, {data_count} data items)")
        print("Ends: falls through (no terminating instruction)")

    # Callers
    jsr_callers = [c for c in callers if c["mnemonic"] == "jsr"]
    branch_callers = [c for c in callers if c["mnemonic"] != "jsr"]

    if jsr_callers:
        print(f"\n### Called by ({len(jsr_callers)} JSR references)")
        for ref in sorted(jsr_callers, key=lambda r: r["addr"]):
            print(f"  &{ref['addr']:04X} JSR  (in {ref['in_sub']})")
    else:
        print(f"\n### Called by (0 JSR references)")

    if branch_callers:
        print(f"\n### Branch entries ({len(branch_callers)} references)")
        for ref in sorted(branch_callers, key=lambda r: r["addr"]):
            print(f"  &{ref['addr']:04X} {ref['mnemonic'].upper():<4s} "
                  f"(in {ref['in_sub']})")

    # Callees
    if callees:
        print(f"\n### Callees ({len(callees)} calls)")
        for ce in callees:
            ext = " [external]" if ce["external"] else ""
            print(f"  &{ce['addr']:04X} {ce['mnemonic'].upper():<4s} "
                  f"{ce['target_label']}{ext}")
    else:
        print(f"\n### Callees (leaf — no calls)")

    # Inline comments
    if inline_comments:
        print(f"\n### Inline comments ({len(inline_comments)} present)")
        for a, comment in inline_comments:
            print(f"  &{a:04X}: {comment}")

    # Assembly listing
    if asm_filepath and Path(asm_filepath).exists():
        asm_lines = Path(asm_filepath).read_text().splitlines(keepends=True)
        addr_to_line, label_to_line = build_index(asm_lines)

        start_target = f"0x{addr:04X}"
        start_line = find_line_for_target(
            start_target, asm_lines, addr_to_line, label_to_line)

        if start_line is not None:
            # Back up to include preceding comment/label lines
            while start_line > 0 and not re.search(
                    r";\s*[0-9a-f]{4}:", asm_lines[start_line - 1]):
                stripped = asm_lines[start_line - 1].strip()
                if (stripped == "" or stripped.startswith(";")
                        or stripped.startswith(".")):
                    start_line -= 1
                else:
                    break

            # Find end: use range_end addr + 1 line, or fixed window
            if range_end is not None:
                end_target = f"0x{range_end:04X}"
                end_line = find_line_for_target(
                    end_target, asm_lines, addr_to_line, label_to_line)
                if end_line is not None:
                    end_line += 1  # Include the terminating instruction
                else:
                    end_line = min(start_line + 80, len(asm_lines))
            else:
                end_line = min(start_line + 80, len(asm_lines))

            print(f"\n### Assembly")
            for i in range(start_line, end_line):
                print(f"{i+1:5d}  {asm_lines[i]}", end="")
            if asm_lines[end_line - 1] and not asm_lines[end_line - 1].endswith("\n"):
                print()

    return 0


def audit(version_dirpath, version, sub_target=None, summary=False,
          flag_filter=None, undeclared=False):
    """Main entry point. Returns exit code 0 on success, 1 on error."""
    from disasm_tools.paths import rom_prefix
    pfx = rom_prefix(version_dirpath)
    json_filepath = version_dirpath / "output" / f"{pfx}-{version}.json"
    asm_filepath = version_dirpath / "output" / f"{pfx}-{version}.asm"

    if not json_filepath.exists():
        print(f"Error: {json_filepath} not found (run disassemble first)",
              file=sys.stderr)
        return 1

    if undeclared:
        candidates = find_undeclared_subs(json_filepath)
        format_undeclared_summary(candidates)
        return 0

    subs = load_subroutines(json_filepath)

    if sub_target:
        sub = find_sub(subs, sub_target, quiet=True)
        if sub is not None:
            format_detail(sub, asm_filepath)
        else:
            return format_undeclared_detail(sub_target, json_filepath,
                                           asm_filepath)
    elif flag_filter:
        if flag_filter.upper() not in ALL_FLAGS:
            print(f"Unknown flag '{flag_filter}'. Available: {', '.join(ALL_FLAGS)}",
                  file=sys.stderr)
            return 1
        format_summary(subs, flag_filter=flag_filter)
    else:
        # Default to summary
        format_summary(subs)

    return 0
