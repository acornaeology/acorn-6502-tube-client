"""Back-propagate annotations from a richly-annotated version to earlier ones.

Uses opcode-level sequence matching (same algorithm as the generate_*.py
scripts) to build a confidence-scored address map between ROM versions,
then propagates inline comments, labels, and subroutine declarations
from the source driver script to the target.
"""

import difflib
import re
import sys
from pathlib import Path

ROM_BASE = 0x8000

OPCODE_LENGTHS = [
    1, 2, 0, 0, 0, 2, 2, 0, 1, 2, 1, 0, 0, 3, 3, 0,
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    3, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    1, 2, 0, 0, 0, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    1, 2, 0, 0, 0, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    0, 2, 0, 0, 2, 2, 2, 0, 1, 0, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 0, 3, 0, 0,
    2, 2, 2, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    2, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
]

# Adjacent version pairs in forward order (older → newer).
# Each entry: (version_a, version_b, reloc_blocks)
# reloc_blocks: list of (src_a, src_b, runtime_dest, length)
VERSION_CHAIN = [
    ("3.34", "3.34B", [
        (0x9307, 0x9308, 0x0016, 0x61),
        (0x934C, 0x934D, 0x0400, 0x100),
        (0x944C, 0x944D, 0x0500, 0x100),
        (0x954C, 0x954D, 0x0600, 0x100),
    ]),
    ("3.34B", "3.35D", [
        (0x9308, 0x931A, 0x0016, 0x61),
        (0x934D, 0x935F, 0x0400, 0x100),
        (0x944D, 0x945F, 0x0500, 0x100),
        (0x954D, 0x955F, 0x0600, 0x100),
    ]),
    ("3.35D", "3.35K", [
        (0x931A, 0x9315, 0x0016, 0x61),
        (0x935F, 0x935A, 0x0400, 0x100),
        (0x945F, 0x945A, 0x0500, 0x100),
        (0x955F, 0x955A, 0x0600, 0x100),
    ]),
    ("3.35K", "3.40", [
        (0x9315, 0x931C, 0x0016, 0x61),
        (0x935A, 0x935D, 0x0400, 0x100),
        (0x945A, 0x9456, 0x0500, 0x100),
        (0x955A, 0x9556, 0x0600, 0x100),
    ]),
    ("3.40", "3.60", [
        (0x931C, 0x9321, 0x0016, 0x61),
        (0x935D, 0x9362, 0x0400, 0x100),
        (0x9456, 0x9462, 0x0500, 0x100),
        (0x9556, 0x9562, 0x0600, 0x100),
    ]),
    ("3.60", "3.62", [
        (0x9321, 0x9321, 0x0016, 0x61),
        (0x9362, 0x9362, 0x0400, 0x100),
        (0x9462, 0x9462, 0x0500, 0x100),
        (0x9562, 0x9562, 0x0600, 0x100),
    ]),
    ("3.62", "3.65", [
        (0x9321, 0x9324, 0x0016, 0x61),
        (0x9362, 0x9365, 0x0400, 0x100),
        (0x9462, 0x9465, 0x0500, 0x100),
        (0x9562, 0x9565, 0x0600, 0x100),
    ]),
]


def disassemble_to_opcodes(data):
    """Linear sweep, returning list of (offset, opcode, length)."""
    instructions = []
    offset = 0
    while offset < len(data):
        opcode = data[offset]
        length = OPCODE_LENGTHS[opcode]
        if length == 0:
            length = 1
        instructions.append((offset, opcode, length))
        offset += length
    return instructions


def _build_confidence_map_for_block(insts_a, insts_b, base_a, base_b):
    """Build {addr_a: (addr_b, block_length)} from two instruction lists.

    base_a/base_b are added to raw offsets to produce final addresses.
    block_length is the number of consecutive matching opcodes in the
    enclosing equal block — the confidence signal.
    """
    opcodes_a = [op for _, op, _ in insts_a]
    opcodes_b = [op for _, op, _ in insts_b]

    matcher = difflib.SequenceMatcher(None, opcodes_a, opcodes_b, autojunk=False)

    conf_map = {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            block_length = i2 - i1
            for k in range(block_length):
                addr_a = base_a + insts_a[i1 + k][0]
                addr_b = base_b + insts_b[j1 + k][0]
                conf_map[addr_a] = (addr_b, block_length)

    return conf_map


def build_confidence_map(data_a, data_b, reloc_blocks):
    """Build a full confidence map between two ROM versions.

    Returns {addr_a: (addr_b, block_length)} covering main ROM code
    and all relocated blocks. Identity-maps RAM workspace addresses.
    """
    insts_a = disassemble_to_opcodes(data_a)
    insts_b = disassemble_to_opcodes(data_b)

    conf_map = _build_confidence_map_for_block(
        insts_a, insts_b, ROM_BASE, ROM_BASE
    )

    for src_a, src_b, dest, length in reloc_blocks:
        block_a = data_a[src_a - ROM_BASE:src_a - ROM_BASE + length]
        block_b = data_b[src_b - ROM_BASE:src_b - ROM_BASE + length]
        reloc_insts_a = disassemble_to_opcodes(block_a)
        reloc_insts_b = disassemble_to_opcodes(block_b)
        reloc_map = _build_confidence_map_for_block(
            reloc_insts_a, reloc_insts_b, dest, dest
        )
        conf_map.update(reloc_map)

    # Identity mappings for RAM workspace labels (high confidence).
    # Exclude addresses within relocated code blocks — those are code,
    # not workspace variables, and must be mapped by opcode matching.
    reloc_ranges = set()
    for _, _, dest, length in reloc_blocks:
        for a in range(dest, dest + length):
            reloc_ranges.add(a)

    high_conf = 1000
    for addr in range(0x0000, 0x0100):
        if addr not in conf_map and addr not in reloc_ranges:
            conf_map[addr] = (addr, high_conf)
    for addr in range(0x0D00, 0x1000):
        if addr not in conf_map:
            conf_map[addr] = (addr, high_conf)

    return conf_map


def build_chained_map(repo_root, source_version, target_version):
    """Build a confidence map from source_version addresses to target_version.

    Chains through adjacent version pairs, inverting maps as needed so
    the result maps source → target. Confidence at each address is the
    minimum block_length across all hops (weakest link).
    """
    # Build ordered list of versions
    versions = [v_a for v_a, _, _ in VERSION_CHAIN] + [VERSION_CHAIN[-1][1]]

    if source_version not in versions or target_version not in versions:
        print(f"Error: unknown version in chain", file=sys.stderr)
        return None

    src_idx = versions.index(source_version)
    tgt_idx = versions.index(target_version)

    if src_idx == tgt_idx:
        print("Error: source and target are the same version", file=sys.stderr)
        return None

    # Walk from source → target through the chain.
    # Each hop always loads ROMs in VERSION_CHAIN order (older, newer)
    # and builds a forward map (older → newer). If source is newer than
    # target, we invert each hop's map after building it.
    if src_idx > tgt_idx:
        # Walk backwards: source is newer, target is older
        chain_indices = list(range(src_idx - 1, tgt_idx - 1, -1))
        invert = True
    else:
        # Walk forwards: source is older, target is newer
        chain_indices = list(range(src_idx, tgt_idx))
        invert = False

    # Build the composed map hop by hop
    composed = None  # {source_addr: (current_addr, min_confidence)}

    for i in chain_indices:
        v_a, v_b, reloc_blocks = VERSION_CHAIN[i]
        # Always load ROMs in VERSION_CHAIN order so reloc_blocks match
        from disasm_tools.paths import resolve_version_dirpath, rom_prefix
        ver_a_dirpath = resolve_version_dirpath(repo_root / "versions", v_a)
        ver_b_dirpath = resolve_version_dirpath(repo_root / "versions", v_b)
        pfx_a = rom_prefix(ver_a_dirpath)
        pfx_b = rom_prefix(ver_b_dirpath)
        rom_a_filepath = ver_a_dirpath / "rom" / f"{pfx_a}-{v_a}.rom"
        rom_b_filepath = ver_b_dirpath / "rom" / f"{pfx_b}-{v_b}.rom"
        data_a = rom_a_filepath.read_bytes()
        data_b = rom_b_filepath.read_bytes()

        hop_map = build_confidence_map(data_a, data_b, reloc_blocks)

        if invert:
            # Invert: {addr_b: (addr_a, conf)} from {addr_a: (addr_b, conf)}
            inv = {}
            for addr_a, (addr_b, conf) in hop_map.items():
                # If multiple addr_a map to same addr_b, keep highest conf
                if addr_b not in inv or conf > inv[addr_b][1]:
                    inv[addr_b] = (addr_a, conf)
            hop_map = inv

        if composed is None:
            composed = hop_map
        else:
            # Compose: for each source_addr in composed, look up
            # its current_addr in hop_map to get the next addr.
            new_composed = {}
            for src_addr, (cur_addr, cur_conf) in composed.items():
                if cur_addr in hop_map:
                    next_addr, hop_conf = hop_map[cur_addr]
                    new_composed[src_addr] = (next_addr, min(cur_conf, hop_conf))
            composed = new_composed

    return composed


# ============================================================
# Annotation parsing
# ============================================================

# Regex for inline comments: comment(0xADDR, "text", inline=True)
RE_INLINE_COMMENT = re.compile(
    r'^comment\(0x([0-9A-Fa-f]+),\s*"((?:[^"\\]|\\.)*)"\s*,\s*inline\s*=\s*True\)',
    re.MULTILINE,
)

# Regex for labels: label(0xADDR, "name")
RE_LABEL = re.compile(
    r'^label\(0x([0-9A-Fa-f]+),\s*"([^"]+)"',
    re.MULTILINE,
)

# Regex for subroutine first line: subroutine(0xADDR, ...)
RE_SUBROUTINE = re.compile(
    r'^subroutine\(0x([0-9A-Fa-f]+)',
    re.MULTILINE,
)


def group_logical_statements(lines):
    """Group lines into logical statements, tracking open parentheses.

    Returns list of (start_line_idx, end_line_idx_exclusive, lines_list).
    """
    groups = []
    current_start = 0
    current_lines = []
    paren_depth = 0
    in_s = None
    escaped = False

    for i, line in enumerate(lines):
        current_lines.append(line)

        code = line
        for j, ch in enumerate(code):
            if in_s is None:
                if ch == '#':
                    break
                if ch in ('"', "'"):
                    if code[j:j+3] in ('"""', "'''"):
                        in_s = code[j:j+3]
                    else:
                        in_s = ch
                elif ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1
            else:
                if not escaped:
                    if len(in_s) == 3 and code[j:j+3] == in_s:
                        in_s = None
                    elif len(in_s) == 1 and ch == in_s:
                        in_s = None
                    elif ch == '\\':
                        escaped = True
                        continue
                escaped = False

        if paren_depth <= 0:
            paren_depth = 0
            groups.append((current_start, i + 1, current_lines))
            current_start = i + 1
            current_lines = []

    if current_lines:
        groups.append((current_start, current_start + len(current_lines),
                       current_lines))

    return groups


def parse_annotations(script_text):
    """Parse a driver script to extract annotations by address.

    Returns:
        inline_comments: {addr: [(text, full_line), ...]}
        labels: {addr: (name, full_line)}  -- last label at each addr
        label_names: set of all label names (across all addrs)
        subroutines: {addr: full_statement_text}
    """
    lines = script_text.split("\n")
    groups = group_logical_statements(lines)

    inline_comments = {}  # addr → list of (text, full_line)
    labels = {}           # addr → (name, full_line) -- last one wins
    label_names = set()   # all label names across all addresses
    subroutines = {}      # addr → full_statement_text (may be multi-line)

    for _start, _end, group_lines in groups:
        first_line = group_lines[0].strip()
        full_text = "\n".join(group_lines)

        # Inline comments
        m = RE_INLINE_COMMENT.match(first_line)
        if m:
            addr = int(m.group(1), 16)
            text = m.group(2)
            inline_comments.setdefault(addr, []).append(
                (text, group_lines[0].rstrip())
            )
            continue

        # Labels
        m = RE_LABEL.match(first_line)
        if m:
            addr = int(m.group(1), 16)
            name = m.group(2)
            labels[addr] = (name, group_lines[0].rstrip())
            label_names.add(name)
            continue

        # Subroutines
        m = RE_SUBROUTINE.match(first_line)
        if m:
            addr = int(m.group(1), 16)
            subroutines[addr] = full_text
            continue

    return inline_comments, labels, label_names, subroutines


def translate_address_in_text(text, old_addr, new_addr):
    """Replace a hex address in annotation text."""
    old_hex = f"0x{old_addr:04X}"
    new_hex = f"0x{new_addr:04X}"
    return text.replace(old_hex, new_hex)


def translate_subroutine(full_text, old_addr, new_addr):
    """Translate the address in a subroutine() statement."""
    old_hex = f"0x{old_addr:04X}"
    new_hex = f"0x{new_addr:04X}"
    # Only replace the first occurrence (the address argument)
    return full_text.replace(old_hex, new_hex, 1)


def backfill(repo_root, source_version, target_version, threshold=5,
             dry_run=False):
    """Propagate annotations from source_version to target_version.

    Returns 0 on success, 1 on error.
    """
    print(f"Building confidence map: {source_version} -> {target_version}...",
          file=sys.stderr)
    conf_map = build_chained_map(repo_root, source_version, target_version)
    if conf_map is None:
        return 1

    total_mapped = len(conf_map)
    above_threshold = sum(1 for _, (_, c) in conf_map.items() if c >= threshold)
    print(f"  {total_mapped} addresses mapped, "
          f"{above_threshold} above threshold ({threshold})",
          file=sys.stderr)

    # Load source annotations
    from disasm_tools.paths import resolve_version_dirpath, rom_prefix
    source_dirpath = resolve_version_dirpath(repo_root / "versions", source_version)
    source_pfx = rom_prefix(source_dirpath)
    source_script_filename = (
        f"disasm_{source_pfx}_{source_version.replace('.', '').lower()}.py"
    )
    source_script_filepath = (
        source_dirpath / "disassemble" / source_script_filename
    )
    print(f"Parsing source annotations from {source_script_filepath.name}...",
          file=sys.stderr)
    source_text = source_script_filepath.read_text()
    src_comments, src_labels, _src_label_names, src_subs = parse_annotations(source_text)
    print(f"  {sum(len(v) for v in src_comments.values())} inline comments, "
          f"{len(src_labels)} labels, {len(src_subs)} subroutines",
          file=sys.stderr)

    # Load target annotations
    target_dirpath = resolve_version_dirpath(repo_root / "versions", target_version)
    target_pfx = rom_prefix(target_dirpath)
    target_script_filename = (
        f"disasm_{target_pfx}_{target_version.replace('.', '').lower()}.py"
    )
    target_script_filepath = (
        target_dirpath / "disassemble" / target_script_filename
    )
    print(f"Parsing target annotations from {target_script_filepath.name}...",
          file=sys.stderr)
    target_text = target_script_filepath.read_text()
    tgt_comments, tgt_labels, tgt_label_names, tgt_subs = parse_annotations(target_text)

    # Build set of target addresses that shouldn't receive new comments.
    # This covers: byte() data marks, and addresses in for-loop entry()
    # calls (which may be overlapping mid-instruction entry points).
    exclude_addrs = set()
    target_lines_raw = target_text.split("\n")
    for i, line in enumerate(target_lines_raw):
        stripped = line.strip()
        # Direct byte() calls
        if stripped.startswith("byte("):
            for m in re.finditer(r'0x([0-9A-Fa-f]{2,5})', stripped):
                exclude_addrs.add(int(m.group(1), 16))
        # for-loop address lists: collect addresses from the header
        # lines of `for addr in [...]` where the body does entry()/byte()
        if stripped.startswith("for ") and "in [" in stripped:
            # Collect all continuation lines until bracket closes
            block = stripped
            j = i + 1
            while "]" not in block and j < len(target_lines_raw):
                block += " " + target_lines_raw[j].strip()
                j += 1
            # Check if body line (after ]:) calls entry() or byte()
            if j < len(target_lines_raw):
                body = target_lines_raw[j].strip()
                if "entry(" in body or "byte(" in body:
                    for m in re.finditer(r'0x([0-9A-Fa-f]{2,5})', block):
                        exclude_addrs.add(int(m.group(1), 16))

    # Build the filtered address map (source_addr → target_addr) for
    # addresses above the confidence threshold
    addr_map = {}  # source_addr → target_addr
    for src_addr, (tgt_addr, conf) in conf_map.items():
        if conf >= threshold:
            addr_map[src_addr] = tgt_addr

    # Find new annotations to propagate
    new_comments = []   # (target_addr, text)
    new_labels = []     # (target_addr, name, trailing_comment)
    new_subs = []       # (target_addr, translated_full_text)

    # Inline comments — skip addresses marked as byte() data
    for src_addr, comment_list in src_comments.items():
        if src_addr not in addr_map:
            continue
        tgt_addr = addr_map[src_addr]
        if tgt_addr in exclude_addrs:
            continue
        for text, _line in comment_list:
            # Skip if target already has a comment at this address
            if tgt_addr in tgt_comments:
                existing_texts = {t for t, _ in tgt_comments[tgt_addr]}
                if text in existing_texts:
                    continue
            new_comments.append((tgt_addr, text))

    # Labels — only propagate if target has no label at the mapped address
    # and the name isn't already used at a different address
    existing_label_names = set(tgt_label_names)
    for src_addr, (name, line) in src_labels.items():
        if src_addr not in addr_map:
            continue
        tgt_addr = addr_map[src_addr]
        if tgt_addr in tgt_labels:
            continue
        if name in existing_label_names:
            continue
        # Extract trailing comment if present
        trailing = ""
        comment_match = re.search(r'(\)\s*#.*)$', line)
        if comment_match:
            trailing = comment_match.group(1)[1:]  # after the )
        new_labels.append((tgt_addr, name, trailing))
        existing_label_names.add(name)

    # Subroutines — propagate if target has no subroutine at mapped addr.
    # If the target has a label() with the same name at the same address,
    # we'll remove that label (subroutine() supersedes it).
    existing_sub_names = set()
    for _, text in tgt_subs.items():
        m = re.search(r'subroutine\(0x[0-9A-Fa-f]+,\s*"([^"]+)"', text)
        if m:
            existing_sub_names.add(m.group(1))
    labels_to_remove = set()  # target addrs whose label() should be removed
    for src_addr, full_text in src_subs.items():
        if src_addr not in addr_map:
            continue
        tgt_addr = addr_map[src_addr]
        if tgt_addr in tgt_subs:
            continue
        m = re.search(r'subroutine\(0x[0-9A-Fa-f]+,\s*"([^"]+)"', full_text)
        if m:
            sub_name = m.group(1)
            if sub_name in existing_sub_names:
                continue
            # If a label with this name exists at the mapped target address,
            # mark it for removal (subroutine() replaces it)
            if sub_name in existing_label_names:
                if tgt_addr in tgt_labels and tgt_labels[tgt_addr][0] == sub_name:
                    labels_to_remove.add(tgt_addr)
                else:
                    # Name conflict at a different address — skip
                    continue
            existing_sub_names.add(sub_name)
            existing_label_names.add(sub_name)
        translated = translate_subroutine(full_text, src_addr, tgt_addr)
        new_subs.append((tgt_addr, translated))

    print(f"\nNew annotations to propagate:", file=sys.stderr)
    print(f"  {len(new_comments)} inline comments", file=sys.stderr)
    print(f"  {len(new_labels)} labels", file=sys.stderr)
    print(f"  {len(new_subs)} subroutines", file=sys.stderr)

    if not new_comments and not new_labels and not new_subs:
        print("Nothing to propagate.", file=sys.stderr)
        return 0

    if dry_run:
        print("\nDry run — not modifying target script.", file=sys.stderr)
        return 0

    # Remove label() calls that will be superseded by new subroutine() calls
    if labels_to_remove:
        print(f"  Removing {len(labels_to_remove)} label(s) superseded by "
              f"subroutines", file=sys.stderr)
        lines = target_text.split("\n")
        kept = []
        for line in lines:
            m = RE_LABEL.match(line.strip())
            if m:
                addr = int(m.group(1), 16)
                if addr in labels_to_remove:
                    continue
            kept.append(line)
        target_text = "\n".join(kept)

    # Insert all new annotations as a block before the "Generate disassembly"
    # section. py8dis is declarative — call order doesn't matter as long as
    # annotations come after load() and move().
    target_lines = target_text.split("\n")

    # Find the "Generate disassembly" section
    insert_idx = len(target_lines)
    for i, line in enumerate(target_lines):
        if "# Generate disassembly" in line:
            # Back up past the section separator line
            idx = i
            while idx > 0 and target_lines[idx - 1].strip().startswith("#"):
                idx -= 1
            # Back up past any preceding blank lines
            while idx > 0 and target_lines[idx - 1].strip() == "":
                idx -= 1
            insert_idx = idx + 1  # Leave one blank line before our block
            break

    # Build the annotation block, sorted by address.
    # Sort order: labels first, then subroutines, then comments at each addr.
    block_lines = []
    block_lines.append("")
    block_lines.append("# " + "=" * 60)
    block_lines.append(f"# Annotations back-propagated from NFS {source_version}")
    block_lines.append("# " + "=" * 60)

    # Collect all annotations with sort keys: (addr, type_order, text)
    # type_order: 0=label, 1=subroutine, 2=comment
    all_annots = []
    for tgt_addr, name, trailing in new_labels:
        line = f'label(0x{tgt_addr:04X}, "{name}")'
        if trailing:
            line += trailing
        all_annots.append((tgt_addr, 0, line))

    for tgt_addr, translated_text in new_subs:
        all_annots.append((tgt_addr, 1, translated_text))

    for tgt_addr, text in new_comments:
        line = f'comment(0x{tgt_addr:04X}, "{text}", inline=True)'
        all_annots.append((tgt_addr, 2, line))

    all_annots.sort(key=lambda x: (x[0], x[1]))

    for _addr, _order, text in all_annots:
        block_lines.append(text)

    # Insert the block
    for i, line in enumerate(block_lines):
        target_lines.insert(insert_idx + i, line)

    result = "\n".join(target_lines)
    target_script_filepath.write_text(result)
    print(f"\nWrote {target_script_filepath}", file=sys.stderr)

    return 0
