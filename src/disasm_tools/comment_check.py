"""Check inline comments against actual instruction data.

Runs mechanical checks on one version's JSON output to find comments
that contradict the instruction they annotate. Reports findings by
confidence level (HIGH = almost certainly wrong, MEDIUM = flag for
human review).
"""

import json
import re
import sys
from pathlib import Path

# Tube register addresses
TUBE_REGISTERS = {
    0xFEE0: "R1", 0xFEE1: "R1",  # status/control
    0xFEE2: "R2", 0xFEE3: "R2",
    0xFEE4: "R3", 0xFEE5: "R3",
    0xFEE6: "R4", 0xFEE7: "R4",
}

# ADLC control register addresses
CR_ADDRESSES = {0xFEA0: "CR1", 0xFEA1: "CR2"}

# Mnemonics that load/modify a register with an immediate operand.
# CMP/CPX/CPY excluded: their comments typically describe what values
# are being compared rather than claiming the operand value.
IMM_REG_MNEMONICS = {
    "lda": "A", "ldx": "X", "ldy": "Y",
    "and": "A", "ora": "A", "eor": "A",
    "adc": "A", "sbc": "A",
}

BRANCH_MNEMONICS = {"bcc", "bcs", "beq", "bne", "bmi", "bpl", "bvc", "bvs"}


def parse_imm_value(operand):
    """Parse an immediate operand like '#&1C' or '#42'. Returns int or None."""
    if not operand or not operand.startswith("#"):
        return None
    val_str = operand[1:]
    if val_str.startswith("&"):
        try:
            return int(val_str[1:], 16)
        except ValueError:
            return None
    if val_str.startswith("$"):
        try:
            return int(val_str[1:], 16)
        except ValueError:
            return None
    try:
        return int(val_str)
    except ValueError:
        return None


def check_reg_value(item, _context):
    """Check if comment claims A=/X=/Y= with a value that doesn't match.

    HIGH confidence: fires when comment says e.g. 'A=&77' but the
    instruction is LDA #&7B.
    """
    comment = item.get("comment_inline", "")
    mnemonic = item.get("mnemonic", "")
    operand = item.get("operand", "")

    if mnemonic not in IMM_REG_MNEMONICS:
        return None

    imm_val = parse_imm_value(operand)
    if imm_val is None:
        return None  # not an immediate instruction (or uses a label)

    expected_reg = IMM_REG_MNEMONICS[mnemonic]

    # Find R=&XX or R=XX or R=&XXXX patterns in comment
    findings = []
    for m in re.finditer(r"\b([AXY])=&([0-9A-Fa-f]+)\b", comment):
        reg, hex_val = m.group(1), m.group(2)
        claimed_val = int(hex_val, 16)
        if reg == expected_reg and claimed_val != imm_val:
            findings.append({
                "check": "reg_value",
                "confidence": "HIGH",
                "addr": item["addr"],
                "message": (f"Comment says {reg}=&{claimed_val:02X} but "
                            f"instruction is {mnemonic.upper()} {operand}"),
            })
        elif reg != expected_reg:
            findings.append({
                "check": "reg_value",
                "confidence": "HIGH",
                "addr": item["addr"],
                "message": (f"Comment says {reg}=&{int(hex_val, 16):02X} but "
                            f"instruction is {mnemonic.upper()} {operand} "
                            f"(sets {expected_reg}, not {reg})"),
            })

    # Also check R=decimal patterns like Y=2
    for m in re.finditer(r"\b([AXY])=(\d+)\b", comment):
        reg, dec_val = m.group(1), int(m.group(2))
        # Skip if this was already caught as hex (e.g. A=&1F also matches A=1F)
        if reg == expected_reg and dec_val != imm_val:
            findings.append({
                "check": "reg_value",
                "confidence": "HIGH",
                "addr": item["addr"],
                "message": (f"Comment says {reg}={dec_val} but "
                            f"instruction is {mnemonic.upper()} {operand}"),
            })
        elif reg != expected_reg:
            findings.append({
                "check": "reg_value",
                "confidence": "HIGH",
                "addr": item["addr"],
                "message": (f"Comment says {reg}={dec_val} but "
                            f"instruction is {mnemonic.upper()} {operand} "
                            f"(sets {expected_reg}, not {reg})"),
            })

    return findings if findings else None


def check_branch_target(item, _context):
    """Check if comment explicitly claims a different branch/jump target.

    Only fires when the comment uses phrasing that indicates the hex address
    IS the target (e.g. "branch to &XXXX", "via &XXXX", "= JSR &XXXX").
    Does NOT fire for incidental hex addresses like "copy to &00C0".

    HIGH confidence.
    """
    comment = item.get("comment_inline", "")
    mnemonic = item.get("mnemonic", "")
    target = item.get("target")

    if mnemonic not in BRANCH_MNEMONICS and mnemonic not in ("jmp", "jsr"):
        return None
    if target is None:
        return None

    # Patterns that indicate the hex address is claimed as the target
    target_claim_patterns = [
        # "branch to &XXXX", "jump to &XXXX", "JSR to &XXXX"
        r"(?:branch|jump|jsr|jmp|goto|go\s+to)\s+(?:to\s+)?&([0-9A-Fa-f]{4})\b",
        # "via &XXXX"
        r"via\s+&([0-9A-Fa-f]{4})\b",
        # "= JSR &XXXX", "= JMP &XXXX"
        r"=\s*(?:JSR|JMP|BNE|BEQ|BCC|BCS|BMI|BPL|BVC|BVS)\s+&([0-9A-Fa-f]{4})\b",
        # "at &XXXX/RTS" or "at &XXXX" when it's a branch
        r"(?:exit|return)\s+(?:at|via)\s+&([0-9A-Fa-f]{4})\b",
    ]

    findings = []
    for pattern in target_claim_patterns:
        for m in re.finditer(pattern, comment, re.IGNORECASE):
            claimed = int(m.group(1), 16)
            if claimed != target:
                findings.append({
                    "check": "branch_target",
                    "confidence": "HIGH",
                    "addr": item["addr"],
                    "message": (f"Comment claims target &{claimed:04X} but "
                                f"{mnemonic.upper()} target is &{target:04X}"),
                })

    return findings if findings else None


def check_cr_value(item, context):
    """Check if comment says CR1=&XX / CR2=&XX but the preceding LDA #imm
    loaded a different value. CR writes are STA to &FEA0/&FEA1.

    HIGH confidence.
    """
    comment = item.get("comment_inline", "")
    mnemonic = item.get("mnemonic", "")
    target = item.get("target")

    if mnemonic != "sta" or target not in CR_ADDRESSES:
        return None

    cr_name = CR_ADDRESSES[target]
    findings = []

    for m in re.finditer(r"\b(CR[12])=&([0-9A-Fa-f]+)\b", comment):
        claimed_cr, hex_val = m.group(1), m.group(2)
        claimed_val = int(hex_val, 16)

        # Check that claimed CR matches the actual register
        if claimed_cr != cr_name:
            findings.append({
                "check": "cr_value",
                "confidence": "HIGH",
                "addr": item["addr"],
                "message": (f"Comment says {claimed_cr}=&{claimed_val:02X} "
                            f"but STA target is {cr_name} (&{target:04X})"),
            })
            continue

        # Find the preceding LDA #imm
        prev_item = context.get("prev_item")
        if prev_item and prev_item.get("mnemonic") == "lda":
            prev_imm = parse_imm_value(prev_item.get("operand", ""))
            if prev_imm is not None and prev_imm != claimed_val:
                findings.append({
                    "check": "cr_value",
                    "confidence": "HIGH",
                    "addr": item["addr"],
                    "message": (f"Comment says {cr_name}=&{claimed_val:02X} "
                                f"but preceding LDA loaded "
                                f"#&{prev_imm:02X}"),
                })

    return findings if findings else None


def check_tube_register(item, _context):
    """Check if comment claims instruction accesses a Tube register that
    doesn't match the operand address.

    Only fires when the comment uses phrasing indicating the instruction
    directly accesses a register (e.g. "read R3", "send via R2", "BIT R1")
    and that register doesn't match the operand target. Does not fire for
    incidental mentions like "WRCH has priority over R2".

    MEDIUM confidence.
    """
    comment = item.get("comment_inline", "")
    target = item.get("target")

    if target is None or not (0xFEE0 <= target <= 0xFEE7):
        return None

    actual_reg = TUBE_REGISTERS[target]

    # Patterns indicating the instruction accesses a specific register
    access_patterns = [
        r"(?:read|write|send|receive|poll|check|BIT|LDA|STA|load|store)\s+R([1-4])\b",
        r"\bR([1-4])\s+(?:status|data|register)\b",
        r"(?:via|from|to)\s+R([1-4])\b",
    ]

    findings = []
    for pattern in access_patterns:
        for m in re.finditer(pattern, comment, re.IGNORECASE):
            claimed_reg = f"R{m.group(1)}"
            if claimed_reg != actual_reg:
                findings.append({
                    "check": "tube_register",
                    "confidence": "MEDIUM",
                    "addr": item["addr"],
                    "message": (f"Comment claims {claimed_reg} access but "
                                f"operand targets {actual_reg} "
                                f"(&{target:04X})"),
                })

    return findings if findings else None


def find_stale_addrs(text, known_addrs):
    """Find &XXXX hex addresses in text that aren't in known_addrs.

    Returns list of int addresses that are stale.
    """
    stale = []
    for m in re.finditer(r"&([0-9A-Fa-f]{4})\b", text):
        addr_val = int(m.group(1), 16)
        if addr_val not in known_addrs:
            stale.append(addr_val)
    return stale


def check_stale_addr(item, context):
    """Check if comment contains &XXXX that doesn't correspond to any
    known address in this version's JSON output.

    MEDIUM confidence.
    """
    comment = item.get("comment_inline", "")
    findings = []
    for addr_val in find_stale_addrs(comment, context["known_addrs"]):
        findings.append({
            "check": "stale_addr",
            "confidence": "MEDIUM",
            "addr": item["addr"],
            "message": (f"Comment contains &{addr_val:04X} which is "
                        f"not a known address in this version"),
        })

    return findings if findings else None


# All checks in order
ALL_CHECKS = [
    check_reg_value,
    check_branch_target,
    check_cr_value,
    check_tube_register,
    check_stale_addr,
]


# Regex to match py8dis auto-generated reference lines
_REFERENCE_LINE_RE = re.compile(
    r"^&[0-9A-Fa-f]+ referenced \d+ times? by "
)


def check_desc_stale_addr(sub, known_addrs):
    """Check subroutine description/title/on_entry/on_exit for stale &XXXX.

    MEDIUM confidence.
    """
    findings = []
    addr = sub["addr"]

    for field in ("description", "title"):
        for stale in find_stale_addrs(sub.get(field, ""), known_addrs):
            findings.append({
                "check": "desc_stale_addr",
                "confidence": "MEDIUM",
                "addr": addr,
                "message": (f"Description contains &{stale:04X} which is "
                            f"not a known address in this version"),
            })

    for field in ("on_entry", "on_exit"):
        obj = sub.get(field)
        if isinstance(obj, dict):
            for _reg, text in obj.items():
                for stale in find_stale_addrs(str(text), known_addrs):
                    findings.append({
                        "check": "desc_stale_addr",
                        "confidence": "MEDIUM",
                        "addr": addr,
                        "message": (f"Description {field} contains "
                                    f"&{stale:04X} which is not a known "
                                    f"address in this version"),
                    })

    return findings


def check_block_stale_addr(item, known_addrs, seen):
    """Check comments_before for stale &XXXX addresses.

    Excludes py8dis-generated reference lines and *** separator lines.
    Skips (addr, stale) pairs already in `seen` to avoid duplicating
    desc_stale_addr findings.

    MEDIUM confidence.
    """
    comments = item.get("comments_before", [])
    if not comments:
        return []

    findings = []
    addr = item["addr"]

    for comment in comments:
        if comment.startswith("*****") or _REFERENCE_LINE_RE.match(comment):
            continue
        for stale in find_stale_addrs(comment, known_addrs):
            if (addr, stale) in seen:
                continue
            findings.append({
                "check": "block_stale_addr",
                "confidence": "MEDIUM",
                "addr": addr,
                "message": (f"Block comment contains &{stale:04X} which is "
                            f"not a known address in this version"),
            })

    return findings


_CHAIN_MNEMONICS = {"iny", "inx", "dey", "dex"}

# Patterns indicating enumeration-style chain comments
_ENUM_PATTERN = re.compile(
    r"(?:Add|Subtract)\s+\d+\s+\(of\s+\d+\)", re.IGNORECASE
)

# Patterns that just restate the mnemonic
_BARE_MNEMONIC_RE = re.compile(
    r"^(?:INY|INX|DEY|DEX)(?:\s*\(.*entry\))?$", re.IGNORECASE
)


def find_chains(sorted_items):
    """Find chains of 2+ consecutive same-mnemonic increment/decrement ops.

    Returns list of chains, each a list of items.
    """
    chains = []
    i = 0
    while i < len(sorted_items):
        item = sorted_items[i]
        mnem = item.get("mnemonic", "")
        if mnem in _CHAIN_MNEMONICS:
            chain = [item]
            j = i + 1
            while (j < len(sorted_items)
                   and sorted_items[j].get("mnemonic") == mnem
                   and sorted_items[j]["addr"] == chain[-1]["addr"] + 1):
                chain.append(sorted_items[j])
                j += 1
            if len(chain) >= 2:
                chains.append(chain)
            i = j
        else:
            i += 1
    return chains


def check_chain_comments(sorted_items, sub_range=None):
    """Check that increment/decrement chains use consistent comment style.

    For chains of 3+ instructions:
    - Each segment-first instruction (entry point) should describe the
      cumulative effect, not just restate the mnemonic.
    - Non-first instructions in a segment should say "(continued)".
    - Enumeration comments like "Add 1 (of 5)" are flagged.

    Chains of exactly 2 are skipped (too short to enforce "(continued)").

    MEDIUM confidence.
    """
    findings = []

    for chain in find_chains(sorted_items):
        # Filter by sub_range
        if sub_range:
            if chain[0]["addr"] < sub_range[0]:
                continue
            if sub_range[1] is not None and chain[0]["addr"] >= sub_range[1]:
                continue

        # Skip 2-instruction chains
        if len(chain) <= 2:
            continue

        # Identify segment boundaries (entry points)
        # Position 0 is always a segment start.
        # Any mid-chain item with references/labels/sub_labels is also one.
        segment_starts = {0}
        for ci, item in enumerate(chain):
            if ci == 0:
                continue
            if (item.get("references")
                    or item.get("labels")
                    or item.get("sub_labels")):
                segment_starts.add(ci)

        for ci, item in enumerate(chain):
            comment = item.get("comment_inline", "")
            addr = item["addr"]

            if ci in segment_starts:
                # Segment-first: should NOT be bare mnemonic or enumeration
                if _BARE_MNEMONIC_RE.match(comment):
                    findings.append({
                        "check": "chain_comment",
                        "confidence": "MEDIUM",
                        "addr": addr,
                        "message": (
                            f"Chain entry comment \"{comment}\" just restates "
                            f"mnemonic; should describe cumulative effect"),
                    })
                if _ENUM_PATTERN.search(comment):
                    findings.append({
                        "check": "chain_comment",
                        "confidence": "MEDIUM",
                        "addr": addr,
                        "message": (
                            f"Chain entry has enumeration comment "
                            f"\"{comment}\"; should describe cumulative "
                            f"effect"),
                    })
            else:
                # Non-first: should be "(continued)" (may have hook-appended
                # text like "; Y=&06" from py8dis auto-tracking)
                if comment and not comment.startswith("(continued)"):
                    findings.append({
                        "check": "chain_comment",
                        "confidence": "MEDIUM",
                        "addr": addr,
                        "message": (
                            f"Mid-chain comment \"{comment}\" should be "
                            f"\"(continued)\""),
                    })

    return findings


def build_known_addrs(data):
    """Build a set of all known addresses for the stale_addr check."""
    known = set()

    # Item addresses
    for item in data["items"]:
        known.add(item["addr"])

    # Subroutine addresses
    for sub in data.get("subroutines", []):
        known.add(sub["addr"])

    # External labels
    for _name, addr in data.get("external_labels", {}).items():
        known.add(addr)

    # Constants
    for const in data.get("constants", []):
        known.add(const["value"])

    # Common OS/hardware addresses not in the JSON
    # Zero page, stack, OS workspace, vectors
    for addr in range(0x0000, 0x0400):
        known.add(addr)
    # Relocated code pages (some versions may not have all items)
    for addr in range(0x0400, 0x0800):
        known.add(addr)
    # NFS workspace pages &0D-&10
    for addr in range(0x0D00, 0x1100):
        known.add(addr)
    # SHEILA, Tube, FRED, JIM, MOS
    for addr in range(0xFC00, 0x10000):
        known.add(addr)

    return known


def run_checks(data, sub_target=None):
    """Run all checks against the JSON data. Returns list of findings."""
    items = data["items"]
    items_by_addr = {item["addr"]: item for item in items}
    sorted_items = sorted(items, key=lambda i: i["addr"])

    known_addrs = build_known_addrs(data)

    # If sub_target specified, find subroutine extent
    sub_range = None
    if sub_target:
        addr_str = sub_target.strip().lstrip("$&").removeprefix("0x")
        try:
            target_addr = int(addr_str, 16)
        except ValueError:
            print(f"Error: invalid address '{sub_target}'", file=sys.stderr)
            return []

        # Find extent: from target_addr to next subroutine
        rom_subs = sorted(
            [s for s in data.get("subroutines", []) if s["addr"] < 0xFF00],
            key=lambda s: s["addr"],
        )
        start = target_addr
        end = None
        for s in rom_subs:
            if s["addr"] > target_addr:
                end = s["addr"]
                break
        sub_range = (start, end)

    findings = []
    prev_item = None

    for item in sorted_items:
        if item.get("type") != "code":
            prev_item = item
            continue
        if not item.get("comment_inline"):
            prev_item = item
            continue

        # Filter by subroutine if requested
        if sub_range:
            if item["addr"] < sub_range[0]:
                prev_item = item
                continue
            if sub_range[1] is not None and item["addr"] >= sub_range[1]:
                break

        context = {
            "prev_item": prev_item,
            "known_addrs": known_addrs,
            "items_by_addr": items_by_addr,
        }

        for check_fn in ALL_CHECKS:
            result = check_fn(item, context)
            if result:
                if isinstance(result, list):
                    findings.extend(result)
                else:
                    findings.append(result)

        prev_item = item

    # Check subroutine descriptions for stale addresses
    # Track (item_addr, stale_addr) pairs to deduplicate against block comments
    desc_seen = set()
    for sub in data.get("subroutines", []):
        if sub_range:
            if sub["addr"] < sub_range[0]:
                continue
            if sub_range[1] is not None and sub["addr"] >= sub_range[1]:
                continue
        desc_findings = check_desc_stale_addr(sub, known_addrs)
        findings.extend(desc_findings)
        # Collect all stale addrs found at this sub's address for dedup
        for field in ("description", "title"):
            for stale in find_stale_addrs(sub.get(field, ""), known_addrs):
                desc_seen.add((sub["addr"], stale))

    # Check block comments (comments_before) for stale addresses
    for item in sorted_items:
        if sub_range:
            if item["addr"] < sub_range[0]:
                continue
            if sub_range[1] is not None and item["addr"] >= sub_range[1]:
                break
        findings.extend(check_block_stale_addr(item, known_addrs, desc_seen))

    # Check increment/decrement chain comments
    findings.extend(check_chain_comments(sorted_items, sub_range=sub_range))

    return findings


def format_findings(findings, summary=False):
    """Print findings grouped by confidence level."""
    high = [f for f in findings if f["confidence"] == "HIGH"]
    medium = [f for f in findings if f["confidence"] == "MEDIUM"]

    if summary:
        print(f"HIGH:   {len(high)} findings")
        print(f"MEDIUM: {len(medium)} findings")
        print(f"Total:  {len(findings)} findings")
        return

    if not findings:
        print("No findings.")
        return

    if high:
        print(f"## HIGH confidence ({len(high)} findings)\n")
        for f in sorted(high, key=lambda x: x["addr"]):
            print(f"  &{f['addr']:04X} [{f['check']}] {f['message']}")
        print()

    if medium:
        print(f"## MEDIUM confidence ({len(medium)} findings)\n")
        for f in sorted(medium, key=lambda x: x["addr"]):
            print(f"  &{f['addr']:04X} [{f['check']}] {f['message']}")
        print()

    print(f"Total: {len(high)} HIGH, {len(medium)} MEDIUM")


def comment_check(version_dirpath, version, sub_target=None, summary=False):
    """Main entry point. Returns exit code 0 on success, 1 on error."""
    from disasm_tools.paths import rom_prefix
    pfx = rom_prefix(version_dirpath)
    json_filepath = version_dirpath / "output" / f"{pfx}-{version}.json"

    if not json_filepath.exists():
        print(f"Error: {json_filepath} not found (run disassemble first)",
              file=sys.stderr)
        return 1

    data = json.loads(Path(json_filepath).read_text())
    findings = run_checks(data, sub_target=sub_target)
    format_findings(findings, summary=summary)

    return 0
