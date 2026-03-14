"""Lint Tube Client ROM disassembly driver scripts and documentation.

Validates that:
1. Every comment(), subroutine(), and label() address in the driver script
   corresponds to a valid address in the py8dis JSON output.
2. Every address_links entry in rom.json has a matching pattern in the
   Markdown document and resolves to a valid address in the referenced
   version's disassembly output.
3. Every glossary_links entry in rom.json has a matching pattern in the
   Markdown document and references a valid term in GLOSSARY.md.
4. The assembly output contains no double-comment lines ("; ;"), which
   indicate a subroutine description placed at an address that py8dis
   is treating as data (e.g. wrong subroutine address, or a data loop
   overrunning into code).
"""

import json
import re
import sys
from pathlib import Path


def extract_annotations(driver_filepath):
    """Extract all annotation addresses from a driver script.

    Parses comment(), subroutine(), and label() calls.
    Returns a list of dicts with keys: kind, address, line_number, detail.
    """
    source = driver_filepath.read_text()
    lines = source.splitlines()
    annotations = []

    for line_number, line in enumerate(lines, 1):
        stripped = line.lstrip()

        # comment(0xADDR, ...)
        m = re.match(r'comment\(\s*(0x[0-9A-Fa-f]+)', stripped)
        if m:
            annotations.append({
                "kind": "comment",
                "address": int(m.group(1), 16),
                "line_number": line_number,
                "detail": None,
            })
            continue

        # subroutine(0xADDR, ...) — also detect is_entry_point=False
        m = re.match(r'subroutine\(\s*(0x[0-9A-Fa-f]+)', stripped)
        if m:
            call_text = line
            paren_depth = line.count('(') - line.count(')')
            j = line_number
            while paren_depth > 0 and j < len(lines):
                call_text += lines[j]
                paren_depth += lines[j].count('(') - lines[j].count(')')
                j += 1

            is_entry_point = "is_entry_point=False" not in call_text
            annotations.append({
                "kind": "subroutine",
                "address": int(m.group(1), 16),
                "line_number": line_number,
                "detail": "entry_point" if is_entry_point else "metadata_only",
            })
            continue

        # label(0xADDR, ...)
        m = re.match(r'label\(\s*(0x[0-9A-Fa-f]+)', stripped)
        if m:
            annotations.append({
                "kind": "label",
                "address": int(m.group(1), 16),
                "line_number": line_number,
                "detail": None,
            })
            continue

    return annotations


def load_valid_addresses(json_filepath):
    """Load valid addresses from the py8dis JSON output.

    Includes item addresses (instructions and data), external label
    addresses (workspace RAM locations named for operand references),
    subroutine addresses (which may be in overlapping code regions
    where the same bytes decode as different instructions depending on
    the entry point), and all ROM-range addresses (to support labels
    at move() block source addresses that py8dis emits as EQU aliases).
    """
    data = json.loads(json_filepath.read_text())
    addresses = {item['addr'] for item in data['items']}
    for item in data['items']:
        for addr_str in item.get('sub_labels', {}):
            addresses.add(int(addr_str))
    for addr in data.get('external_labels', {}).values():
        addresses.add(addr)
    for sub in data.get('subroutines', []):
        addresses.add(sub['addr'])
    load_addr = data['meta']['load_addr']
    end_addr = data['meta']['end_addr']
    addresses.update(range(load_addr, end_addr))
    return addresses


def find_repo_root(start_path):
    """Find the repository root by looking for pyproject.toml."""
    dirpath = Path(start_path).resolve()
    while dirpath != dirpath.parent:
        if (dirpath / "pyproject.toml").exists():
            return dirpath
        dirpath = dirpath.parent
    raise RuntimeError("Could not find repository root")


def load_address_ranges(json_filepath):
    """Build address ranges covered by the disassembly.

    Returns a list of (start, end) tuples representing contiguous address
    ranges. Doc addresses are valid if they fall within any range.
    """
    data = json.loads(json_filepath.read_text())
    item_addrs = sorted(item['addr'] for item in data['items'])
    if not item_addrs:
        return []

    meta = data.get('meta', {})
    load_addr = meta.get('load_addr', 0xF800)
    end_addr = meta.get('end_addr', load_addr + 0x0800)
    ranges = [(load_addr, end_addr - 1)]

    all_addrs = set()
    for addr in item_addrs:
        if addr < load_addr or addr >= end_addr:
            all_addrs.add(addr)
    for sub in data.get('subroutines', []):
        all_addrs.add(sub['addr'])

    sorted_addrs = sorted(all_addrs)
    if sorted_addrs:
        block_start = sorted_addrs[0]
        block_end = sorted_addrs[0]

        for addr in sorted_addrs[1:]:
            if addr - block_end > 256:
                ranges.append((block_start, block_end + 32))
                block_start = addr
            block_end = addr

        ranges.append((block_start, block_end + 16))

    return ranges


def address_in_ranges(address, ranges):
    """Check if an address falls within any of the given ranges."""
    return any(start <= address <= end for start, end in ranges)


def find_code_block_ranges(md_text):
    """Find character offset ranges of fenced code blocks in Markdown."""
    ranges = []
    in_block = False
    block_start = 0
    offset = 0
    for line in md_text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if not in_block:
                block_start = offset
                in_block = True
            else:
                ranges.append((block_start, offset + len(line)))
                in_block = False
        offset += len(line)
    return ranges


def offset_in_code_block(offset, code_block_ranges):
    """Check if a character offset falls inside any fenced code block."""
    return any(start <= offset < end for start, end in code_block_ranges)


def find_nth_occurrence(text, pattern, n):
    """Find the character offset of the nth occurrence of pattern in text."""
    start = 0
    for _ in range(n + 1):
        pos = text.find(pattern, start)
        if pos == -1:
            return -1
        start = pos + 1
    return pos


def lint_docs(version_dirpath, version):
    """Validate address_links in rom.json against Markdown docs and JSON outputs."""
    rom_json_filepath = version_dirpath / "rom" / "rom.json"
    if not rom_json_filepath.exists():
        return [], 0

    rom_meta = json.loads(rom_json_filepath.read_text())
    docs = rom_meta.get("docs", [])
    if not docs:
        return [], 0

    repo_root = find_repo_root(version_dirpath)
    ranges_cache = {}

    def get_ranges(ver):
        if ver not in ranges_cache:
            from disasm_tools.paths import resolve_version_dirpath, rom_prefix
            ver_dirpath = resolve_version_dirpath(repo_root / "versions", ver)
            pfx = rom_prefix(ver_dirpath)
            json_fp = ver_dirpath / "output" / f"{pfx}-{ver}.json"
            if json_fp.exists():
                ranges_cache[ver] = load_address_ranges(json_fp)
            else:
                ranges_cache[ver] = None
        return ranges_cache[ver]

    errors = []
    link_count = 0

    for doc in docs:
        address_links = doc.get("address_links", [])
        if not address_links:
            continue

        doc_filepath = version_dirpath / doc["path"]
        if not doc_filepath.exists():
            errors.append(f"  {doc['path']}: file not found")
            continue

        md_text = doc_filepath.read_text()
        code_blocks = find_code_block_ranges(md_text)

        for link in address_links:
            link_count += 1
            pattern = link["pattern"]
            occurrence = link["occurrence"]
            ver = link["version"]
            address = int(link["address"], 16)

            count = md_text.count(pattern)
            if occurrence >= count:
                errors.append(
                    f"  {doc['path']}: pattern \"{pattern}\" occurrence "
                    f"{occurrence} not found (only {count} occurrence(s))"
                )
                continue

            match_offset = find_nth_occurrence(md_text, pattern, occurrence)
            if match_offset >= 0 and offset_in_code_block(match_offset, code_blocks):
                errors.append(
                    f"  {doc['path']}: \"{pattern}\" occurrence "
                    f"{occurrence} is inside a fenced code block"
                )
                continue

            ranges = get_ranges(ver)
            if ranges is None:
                errors.append(
                    f"  {doc['path']}: \"{pattern}\" references version "
                    f"{ver} but no JSON output found"
                )
            elif not address_in_ranges(address, ranges):
                errors.append(
                    f"  {doc['path']}: \"{pattern}\" -> {ver} "
                    f"0x{address:04X} is outside all disassembly ranges"
                )

    return errors, link_count


def parse_glossary_terms(glossary_filepath):
    """Extract term names from GLOSSARY.md."""
    terms = set()
    for line in glossary_filepath.read_text().splitlines():
        m = re.match(r'\*\*(.+?)\*\*', line)
        if m:
            terms.add(m.group(1))
    return terms


def lint_glossary_links(version_dirpath):
    """Validate glossary_links in rom.json against Markdown docs and GLOSSARY.md."""
    rom_json_filepath = version_dirpath / "rom" / "rom.json"
    if not rom_json_filepath.exists():
        return [], 0

    rom_meta = json.loads(rom_json_filepath.read_text())
    docs = rom_meta.get("docs", [])
    if not docs:
        return [], 0

    repo_root = find_repo_root(version_dirpath)
    glossary_filepath = repo_root / "GLOSSARY.md"
    if not glossary_filepath.exists():
        return [], 0

    glossary_terms = parse_glossary_terms(glossary_filepath)

    errors = []
    link_count = 0

    for doc in docs:
        glossary_links = doc.get("glossary_links", [])
        if not glossary_links:
            continue

        doc_filepath = version_dirpath / doc["path"]
        if not doc_filepath.exists():
            errors.append(f"  {doc['path']}: file not found")
            continue

        md_text = doc_filepath.read_text()
        code_blocks = find_code_block_ranges(md_text)

        for link in glossary_links:
            link_count += 1
            pattern = link["pattern"]
            occurrence = link["occurrence"]
            term = link["term"]

            count = md_text.count(pattern)
            if occurrence >= count:
                errors.append(
                    f"  {doc['path']}: pattern \"{pattern}\" occurrence "
                    f"{occurrence} not found (only {count} occurrence(s))"
                )
                continue

            match_offset = find_nth_occurrence(md_text, pattern, occurrence)
            if match_offset >= 0 and offset_in_code_block(match_offset, code_blocks):
                errors.append(
                    f"  {doc['path']}: glossary \"{pattern}\" occurrence "
                    f"{occurrence} is inside a fenced code block"
                )
                continue

            if term not in glossary_terms:
                errors.append(
                    f"  {doc['path']}: glossary term \"{term}\" "
                    f"not found in GLOSSARY.md"
                )

    return errors, link_count


def lint_double_comments(asm_filepath):
    """Check assembly output for double-comment and overlapping lines."""
    if not asm_filepath.exists():
        return []

    errors = []
    for line_number, line in enumerate(asm_filepath.read_text().splitlines(), 1):
        addr_match = re.search(r';\s+([0-9a-f]{4}):', line)
        addr_str = f" at &{addr_match.group(1).upper()}" if addr_match else ""

        if re.match(r'^;\s+;', line):
            errors.append(
                f"  asm line {line_number}: double comment{addr_str}"
                f" — subroutine description inside data"
            )
        elif re.match(r'^; overlapping:', line):
            errors.append(
                f"  asm line {line_number}: overlapping comment{addr_str}"
                f" — tracer reached data region"
            )
    return errors


def lint(version_dirpath, version):
    """Validate annotation addresses against the JSON output.

    Returns 0 on success, 1 on failure.
    """
    from disasm_tools.paths import rom_prefix
    pfx = rom_prefix(version_dirpath)
    script_filename = f"disasm_{pfx.replace('-', '_')}_{version.replace('.', '').lower()}.py"
    driver_filepath = version_dirpath / "disassemble" / script_filename
    json_filepath = version_dirpath / "output" / f"{pfx}-{version}.json"

    if not driver_filepath.exists():
        print(f"Error: driver script not found: {driver_filepath}", file=sys.stderr)
        return 1

    if not json_filepath.exists():
        print(f"Error: JSON output not found: {json_filepath}", file=sys.stderr)
        print("Run 'acorn-tube-client-disasm-tool disassemble' first.", file=sys.stderr)
        return 1

    annotations = extract_annotations(driver_filepath)
    valid_addresses = load_valid_addresses(json_filepath)

    counts = {"comment": 0, "subroutine": 0, "label": 0}
    errors = []
    warnings = []

    for ann in annotations:
        counts[ann["kind"]] += 1

        if ann["address"] not in valid_addresses:
            msg = (
                f"  line {ann['line_number']}: "
                f"{ann['kind']}(0x{ann['address']:04X}) "
                f"— not a valid item address"
            )

            if ann["kind"] == "subroutine" and ann["detail"] == "metadata_only":
                warnings.append(msg)
            else:
                errors.append(msg)

    # Lint documentation address links
    doc_errors, doc_link_count = lint_docs(version_dirpath, version)

    # Lint glossary links
    glossary_errors, glossary_link_count = lint_glossary_links(version_dirpath)

    # Lint assembly output for double-comment artefacts
    asm_filepath = version_dirpath / "output" / f"{pfx}-{version}.asm"
    double_comment_errors = lint_double_comments(asm_filepath)

    failed = False

    if errors:
        print(
            f"Lint FAILED: {len(errors)} annotation(s) at invalid addresses ({version})",
            file=sys.stderr,
        )
        for msg in errors:
            print(msg, file=sys.stderr)
        if warnings:
            print(
                f"\n  Plus {len(warnings)} warning(s) "
                f"(is_entry_point=False subroutines):",
                file=sys.stderr,
            )
            for msg in warnings:
                print(msg, file=sys.stderr)
        failed = True

    if doc_errors:
        print(
            f"Lint FAILED: {len(doc_errors)} address_link error(s) ({version})",
            file=sys.stderr,
        )
        for msg in doc_errors:
            print(msg, file=sys.stderr)
        failed = True

    if glossary_errors:
        print(
            f"Lint FAILED: {len(glossary_errors)} glossary_link error(s) ({version})",
            file=sys.stderr,
        )
        for msg in glossary_errors:
            print(msg, file=sys.stderr)
        failed = True

    if double_comment_errors:
        print(
            f"Lint FAILED: {len(double_comment_errors)} double-comment line(s) "
            f"in assembly output ({version})",
            file=sys.stderr,
        )
        for msg in double_comment_errors:
            print(msg, file=sys.stderr)
        failed = True

    if failed:
        return 1

    summary = (
        f"{counts['comment']} comments, "
        f"{counts['subroutine']} subroutines, "
        f"{counts['label']} labels"
    )
    if doc_link_count:
        summary += f", {doc_link_count} doc address links"
    if glossary_link_count:
        summary += f", {glossary_link_count} glossary links"
    summary += " checked"
    print(f"Lint passed: {summary} ({version})")

    if warnings:
        print(f"  {len(warnings)} warning(s) (is_entry_point=False subroutines):")
        for msg in warnings:
            print(msg)

    return 0
