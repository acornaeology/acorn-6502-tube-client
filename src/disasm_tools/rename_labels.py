"""Batch rename auto-generated labels in py8dis driver scripts.

Given a list of (address, new_name) pairs, inserts label() declarations
into the "Code label renames" section of the driver script in address order.

Also supports --sub mode to list all auto-generated labels within a
subroutine's extent with assembly context.
"""

import json
import re
import sys
from pathlib import Path

from disasm_tools.audit import build_memory_regions, load_subroutines, region_for_addr
from disasm_tools.asm_extract import build_index, find_line_for_target
from disasm_tools.labels import AUTO_LABEL_RE, _collect_auto_labels


# Matches label(0xABCD, "name")
LABEL_RE = re.compile(r'^label\(0x([0-9A-Fa-f]+),\s*"([^"]*)"')

# Section header pattern
SECTION_RE = re.compile(r'^# =+')
RENAME_SECTION_RE = re.compile(r'^# Code label renames')


def _parse_label_declarations(lines):
    """Parse all label() declarations from driver script lines.

    Returns list of dicts: addr, name, line_idx (0-indexed).
    """
    declarations = []
    for i, line in enumerate(lines):
        m = LABEL_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            name = m.group(2)
            declarations.append({"addr": addr, "name": name, "line_idx": i})
    return declarations


def _find_rename_section(lines):
    """Find the "Code label renames" section boundaries.

    Returns (section_start, section_end) as 0-indexed line numbers.
    section_start is the "# ===..." line before the title.
    section_end is the line before the next "# ===..." section header.
    """
    header_line = None
    for i, line in enumerate(lines):
        if RENAME_SECTION_RE.match(line):
            # The separator line is one line before
            header_line = i - 1 if i > 0 and SECTION_RE.match(lines[i - 1]) else i
            break

    if header_line is None:
        return None, None

    # Find the end of the section (next "# ===..." line)
    section_end = len(lines)
    # Skip the header block (separator, title, separator)
    body_start = header_line + 3
    for i in range(body_start, len(lines)):
        if SECTION_RE.match(lines[i]):
            section_end = i
            break

    return header_line, section_end


def _find_insert_position(lines, section_start, section_end, target_addr):
    """Find the line index to insert a label at target_addr within the section.

    Returns the 0-indexed line where the new label() call should go.
    Labels are inserted in address order among existing labels in the section.
    """
    # Find all existing labels in the section
    section_labels = []
    for i in range(section_start, section_end):
        m = LABEL_RE.match(lines[i])
        if m:
            addr = int(m.group(1), 16)
            section_labels.append({"addr": addr, "line_idx": i})

    if not section_labels:
        # Empty section, insert after header (skip blank lines)
        insert = section_start + 3  # after separator + title + separator
        while insert < section_end and lines[insert].strip() == "":
            insert += 1
        # Insert after any comment lines
        while (insert < section_end and lines[insert].strip().startswith("#")
               and not SECTION_RE.match(lines[insert])):
            insert += 1
        while insert < section_end and lines[insert].strip() == "":
            insert += 1
        return insert

    # Find the right position by address
    for sl in section_labels:
        if sl["addr"] > target_addr:
            return sl["line_idx"]

    # After all existing labels
    last = section_labels[-1]["line_idx"]
    return last + 1


def rename_labels(driver_filepath, renames):
    """Apply label renames to a driver script.

    Args:
        driver_filepath: Path to the py8dis driver script.
        renames: List of (addr, new_name) tuples.

    Returns exit code (0 success, 1 error).
    """
    driver_filepath = Path(driver_filepath)
    lines = driver_filepath.read_text().splitlines()

    # Check for existing label declarations at these addresses
    existing = _parse_label_declarations(lines)
    existing_addrs = {d["addr"]: d for d in existing}

    # Find the rename section
    section_start, section_end = _find_rename_section(lines)
    if section_start is None:
        print("Error: 'Code label renames' section not found in driver",
              file=sys.stderr)
        return 1

    # Validate renames
    errors = []
    for addr, name in renames:
        if addr in existing_addrs:
            ex = existing_addrs[addr]
            errors.append(
                f"  &{addr:04X}: already declared as '{ex['name']}' "
                f"at line {ex['line_idx'] + 1}"
            )

    if errors:
        print("Error: labels already declared:", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    # Sort renames by address (descending) so line numbers stay valid
    # as we insert from bottom to top
    sorted_renames = sorted(renames, key=lambda r: r[0], reverse=True)

    inserted = 0
    for addr, name in sorted_renames:
        # Recalculate section end after each insertion
        _, section_end = _find_rename_section(lines)
        insert_line = _find_insert_position(
            lines, section_start, section_end, addr)
        new_line = f'label(0x{addr:04X}, "{name}")'
        lines.insert(insert_line, new_line)
        inserted += 1

    driver_filepath.write_text("\n".join(lines) + "\n")
    print(f"Inserted {inserted} label(s) into {driver_filepath.name}")
    return 0


def show_sub_labels(version_dirpath, version, sub_target):
    """Show all auto-generated labels within a subroutine's extent.

    Prints each auto-generated label with surrounding assembly context
    to facilitate batch naming.

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

    data = json.loads(json_filepath.read_text())
    items = data["items"]
    memory_regions = build_memory_regions(data.get("meta", {}))

    # Load subroutines
    audit_subs = load_subroutines(json_filepath)
    subs_by_name = {s["name"]: s for s in audit_subs}
    subs_by_addr = {s["addr"]: s for s in audit_subs}

    # Resolve sub_target to a subroutine
    target_sub = None
    # Try as address first
    addr_str = sub_target.strip().lstrip("$&").removeprefix("0x")
    try:
        target_addr = int(addr_str, 16)
        target_sub = subs_by_addr.get(target_addr)
    except ValueError:
        pass
    # Try as name
    if target_sub is None:
        target_sub = subs_by_name.get(sub_target)
    if target_sub is None:
        print(f"Subroutine '{sub_target}' not found", file=sys.stderr)
        return 1

    sub_addr = target_sub["addr"]
    sub_name = target_sub["name"]
    sub_region = region_for_addr(sub_addr, memory_regions)

    # Find the next subroutine in the same region
    sorted_subs = sorted(audit_subs, key=lambda s: s["addr"])
    next_sub_addr = None
    found = False
    for s in sorted_subs:
        if found:
            s_region = region_for_addr(s["addr"], memory_regions)
            if s_region == sub_region:
                next_sub_addr = s["addr"]
                break
        if s["addr"] == sub_addr:
            found = True

    # Collect auto-generated labels within this sub's extent
    auto_labels = _collect_auto_labels(items)
    sub_labels = []
    for label_name, label_addr in auto_labels:
        if label_addr < sub_addr:
            continue
        if next_sub_addr is not None and label_addr >= next_sub_addr:
            continue
        label_region = region_for_addr(label_addr, memory_regions)
        if label_region != sub_region:
            continue
        sub_labels.append((label_name, label_addr))

    sub_labels.sort(key=lambda x: x[1])

    if not sub_labels:
        print(f"No auto-generated labels in {sub_name} (&{sub_addr:04X})")
        return 0

    # Load ASM for context
    asm_lines = asm_filepath.read_text().splitlines(keepends=True)
    addr_to_line, label_to_line = build_index(asm_lines)

    # Print header
    extent_str = f"&{sub_addr:04X}"
    if next_sub_addr:
        extent_str += f"-&{next_sub_addr - 1:04X}"
    print(f"Auto-generated labels in {sub_name} ({extent_str}): "
          f"{len(sub_labels)}")
    print()

    # Print each label with context
    for label_name, label_addr in sub_labels:
        target = f"0x{label_addr:04X}"
        center_line = find_line_for_target(
            target, asm_lines, addr_to_line, label_to_line)

        print(f"--- {label_name} (&{label_addr:04X}) ---")
        if center_line is not None:
            start = max(0, center_line - 3)
            end = min(len(asm_lines), center_line + 5)
            for i in range(start, end):
                marker = ">>>" if i == center_line else "   "
                print(f"  {marker} {asm_lines[i].rstrip()}")
        print()

    # Print rename template
    print("=" * 60)
    print("RENAME TEMPLATE (copy to renames file, edit names):")
    print("=" * 60)
    for label_name, label_addr in sub_labels:
        print(f"{label_addr:04x} {label_name}")

    return 0
