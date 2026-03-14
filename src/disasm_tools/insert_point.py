"""Find insertion points for new subroutine() declarations in driver scripts.

Parses a py8dis driver script to locate all existing subroutine() declarations,
identifies the main address-ordered block, and computes where a new declaration
for a given address should be inserted.
"""

import re
import sys
from pathlib import Path


# Matches the start of a subroutine() call with a hex address
SUB_RE = re.compile(r'^subroutine\(0x([0-9A-Fa-f]+)')

# Section header pattern (line of ===)
SECTION_RE = re.compile(r'^# =+')


def _find_call_end(lines, start_line):
    """Find the line index of the closing ')' for a call starting at start_line."""
    depth = 0
    for i in range(start_line, len(lines)):
        for ch in lines[i]:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return i
    return start_line


def parse_subroutine_declarations(lines):
    """Parse all subroutine() declarations from driver script lines.

    Returns a list of dicts with: addr, name, start_line, end_line (0-indexed).
    """
    declarations = []
    for i, line in enumerate(lines):
        m = SUB_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            # Extract name: second argument (string) or name= keyword
            name_match = re.search(r'subroutine\(0x[0-9A-Fa-f]+,\s*"([^"]*)"',
                                   line)
            if not name_match:
                # Try hook=None style with name= keyword
                name_match = re.search(r'name="([^"]*)"', line)
            name = name_match.group(1) if name_match else None
            end_line = _find_call_end(lines, i)
            declarations.append({
                "addr": addr,
                "name": name,
                "start_line": i,
                "end_line": end_line,
            })
    return declarations


def find_main_block(lines, declarations):
    """Identify the main address-ordered subroutine block.

    Returns (block_start_line, block_end_line) as 0-indexed line numbers
    bounding the main block. The block is identified by the section header
    comment '# Subroutines' or by finding the largest address-ordered run.
    """
    # Try to find the section header
    header_line = None
    for i, line in enumerate(lines):
        if '# Subroutines' in line and ('correspondence' in line
                                        or 'subroutines' in line.lower()):
            header_line = i
            break

    if header_line is None:
        # Fallback: find the first subroutine() declaration
        if declarations:
            header_line = declarations[0]["start_line"] - 1
        else:
            return 0, len(lines) - 1

    # Find the next section separator after the last declaration in this block
    # The block ends at the next "# ====" line after the header
    block_start = header_line
    block_end = len(lines) - 1

    # Find declarations that are in the address-ordered run after the header
    after_header = [d for d in declarations if d["start_line"] > header_line]
    if not after_header:
        return block_start, block_end

    # Find where the next section starts (next "# ====" after the first decl)
    first_decl_line = after_header[0]["start_line"]
    for i in range(first_decl_line + 1, len(lines)):
        if SECTION_RE.match(lines[i]):
            block_end = i - 1
            break

    return block_start, block_end


def find_insert_point(driver_filepath, target_addr):
    """Find where to insert a subroutine() declaration for target_addr.

    Prints the insertion point and surrounding context. Returns exit code.
    """
    lines = Path(driver_filepath).read_text().splitlines()
    declarations = parse_subroutine_declarations(lines)

    if not declarations:
        print("Error: no subroutine() declarations found in driver",
              file=sys.stderr)
        return 1

    # Check if already declared
    for d in declarations:
        if d["addr"] == target_addr:
            name = d["name"] or "(unnamed)"
            print(f"Already declared: subroutine(0x{target_addr:04X}, "
                  f"\"{name}\", ...) at line {d['start_line'] + 1}")
            return 1

    # Find the main block
    block_start, block_end = find_main_block(lines, declarations)

    # Get declarations within the main block, sorted by address
    main_decls = sorted(
        [d for d in declarations
         if block_start <= d["start_line"] <= block_end],
        key=lambda d: d["addr"],
    )

    if not main_decls:
        print("Error: no declarations found in main block", file=sys.stderr)
        return 1

    # Find predecessor and successor by address
    pred = None
    succ = None
    for d in main_decls:
        if d["addr"] < target_addr:
            pred = d
        elif d["addr"] > target_addr and succ is None:
            succ = d

    # Compute insertion line
    if pred is not None:
        insert_after = pred["end_line"]
        pred_name = pred["name"] or f"&{pred['addr']:04X}"
    else:
        # Before all declarations in the block — insert at block start
        insert_after = main_decls[0]["start_line"] - 1
        pred_name = "(start of block)"

    if succ is not None:
        succ_name = succ["name"] or f"&{succ['addr']:04X}"
    else:
        succ_name = "(end of block)"

    insert_line = insert_after + 1  # 0-indexed line where new text goes

    # Print result
    print(f"Insert subroutine(0x{target_addr:04X}, ...) at line "
          f"{insert_line + 1}")
    if pred:
        print(f"After: {pred_name} (&{pred['addr']:04X}) "
              f"line {pred['start_line'] + 1}")
    if succ:
        print(f"Before: {succ_name} (&{succ['addr']:04X}) "
              f"line {succ['start_line'] + 1}")

    # Show surrounding context with insertion marker on its own line
    ctx_start = max(0, insert_after - 4)
    ctx_end = min(len(lines), insert_line + 6)

    print()
    for i in range(ctx_start, ctx_end):
        if i == insert_line:
            print("       >>> INSERT HERE <<<")
        print(f"{i + 1:5d}  {lines[i]}")

    return 0
