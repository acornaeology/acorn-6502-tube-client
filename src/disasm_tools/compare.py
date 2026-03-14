"""ROM binary comparison tool using difflib.SequenceMatcher.

Compares two ROM images at three levels of granularity:
byte-level, opcode-only (ignoring operands), and full instruction (opcode +
operands). Produces a human-readable report showing where the ROMs differ.
"""

import hashlib
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from disasm_tools.mos6502 import OPCODE_LENGTHS, OPCODE_MNEMONICS, ROM_BASE


# ============================================================
# Data structures
# ============================================================


@dataclass
class Instruction:
    """A single 6502 instruction from linear sweep disassembly."""

    offset: int
    opcode: int
    operand_bytes: bytes
    length: int
    is_valid: bool

    @property
    def rom_address(self) -> int:
        return ROM_BASE + self.offset

    @property
    def all_bytes(self) -> bytes:
        return bytes([self.opcode]) + self.operand_bytes

    @property
    def mnemonic(self) -> str:
        if not self.is_valid:
            return "???"
        return OPCODE_MNEMONICS[self.opcode]


# ============================================================
# Linear sweep disassembly
# ============================================================


def disassemble_linear(data: bytes) -> list[Instruction]:
    """Decompose ROM bytes into instructions using linear sweep.

    Invalid opcodes (length 0 in the table) are emitted as single-byte
    data items. This is a deliberate simplification: both ROMs are swept
    identically, so data tables misinterpreted as instructions will align
    correctly in the SequenceMatcher.
    """
    instructions = []
    offset = 0
    while offset < len(data):
        opcode = data[offset]
        length = OPCODE_LENGTHS[opcode]
        if length == 0:
            instructions.append(
                Instruction(offset, opcode, b"", 1, is_valid=False)
            )
            offset += 1
        elif offset + length > len(data):
            # Truncated at end of ROM
            operand = data[offset + 1 :]
            instructions.append(
                Instruction(offset, opcode, bytes(operand), len(operand) + 1,
                            is_valid=False)
            )
            break
        else:
            operand = data[offset + 1 : offset + length]
            instructions.append(
                Instruction(offset, opcode, bytes(operand), length,
                            is_valid=True)
            )
            offset += length
    return instructions


# ============================================================
# Formatting helpers
# ============================================================


def format_address(offset: int) -> str:
    """Format a ROM offset as a $hex address."""
    return f"${ROM_BASE + offset:04X}"


def format_instruction(inst: Instruction) -> str:
    """Format a single instruction for display."""
    hex_bytes = " ".join(f"{b:02X}" for b in inst.all_bytes)
    if not inst.is_valid:
        return f".byte ${inst.opcode:02X}  ({hex_bytes})"

    mnemonic = inst.mnemonic
    if inst.length == 1:
        return f"{mnemonic}  ({hex_bytes})"
    elif inst.length == 2:
        operand = inst.operand_bytes[0]
        if inst.opcode in (
            0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0,
        ):
            signed = operand if operand < 128 else operand - 256
            target = inst.rom_address + 2 + signed
            return f"{mnemonic} ${target:04X}  ({hex_bytes})"
        else:
            return f"{mnemonic} ${operand:02X}  ({hex_bytes})"
    else:
        addr = inst.operand_bytes[0] | (inst.operand_bytes[1] << 8)
        return f"{mnemonic} ${addr:04X}  ({hex_bytes})"


# ============================================================
# Comparison engine
# ============================================================


def compare_roms(
    data_a: bytes, data_b: bytes, label_a: str, label_b: str
) -> str:
    """Generate the full comparison report."""
    lines = []

    sha256_a = hashlib.sha256(data_a).hexdigest()
    sha256_b = hashlib.sha256(data_b).hexdigest()

    byte_matcher = SequenceMatcher(None, data_a, data_b, autojunk=False)
    byte_ratio = byte_matcher.ratio()
    identical_bytes = sum(
        1 for a, b in zip(data_a, data_b) if a == b
    )

    insts_a = disassemble_linear(data_a)
    insts_b = disassemble_linear(data_b)

    opcodes_a = [inst.opcode for inst in insts_a]
    opcodes_b = [inst.opcode for inst in insts_b]
    opcode_matcher = SequenceMatcher(None, opcodes_a, opcodes_b, autojunk=False)
    opcode_ratio = opcode_matcher.ratio()

    inst_bytes_a = [inst.all_bytes for inst in insts_a]
    inst_bytes_b = [inst.all_bytes for inst in insts_b]
    inst_matcher = SequenceMatcher(None, inst_bytes_a, inst_bytes_b, autojunk=False)
    inst_ratio = inst_matcher.ratio()

    lines.append("=" * 64)
    lines.append(f"ROM Comparison: {label_a} vs {label_b}")
    lines.append("=" * 64)
    lines.append("")

    lines.append("1. SUMMARY")
    lines.append("")
    lines.append(f"  {label_a}: {len(data_a)} bytes  SHA-256: {sha256_a[:16]}...")
    lines.append(f"  {label_b}: {len(data_b)} bytes  SHA-256: {sha256_b[:16]}...")
    lines.append("")
    min_len = min(len(data_a), len(data_b))
    lines.append(
        f"  Identical bytes at same offset: {identical_bytes}/{min_len} "
        f"({100 * identical_bytes / min_len:.1f}%)"
    )
    lines.append(f"  Byte-level similarity:         {byte_ratio:.1%} (SequenceMatcher)")
    lines.append(f"  Opcode-level similarity:       {opcode_ratio:.1%} (structure only)")
    lines.append(
        f"  Full instruction similarity:   {inst_ratio:.1%} (opcode + operands)"
    )
    lines.append(f"  Instructions: {len(insts_a)} ({label_a}) / {len(insts_b)} ({label_b})")
    lines.append("")

    lines.append("2. STRUCTURAL CHANGES (opcode-level)")
    lines.append("")

    opcode_ops = opcode_matcher.get_opcodes()
    n_equal = sum(1 for tag, *_ in opcode_ops if tag == "equal")
    n_replace = sum(1 for tag, *_ in opcode_ops if tag == "replace")
    n_delete = sum(1 for tag, *_ in opcode_ops if tag == "delete")
    n_insert = sum(1 for tag, *_ in opcode_ops if tag == "insert")
    n_changes = n_replace + n_delete + n_insert

    lines.append(
        f"  {n_changes} change blocks "
        f"({n_replace} replaced, {n_delete} deleted, {n_insert} inserted), "
        f"{n_equal} equal regions"
    )
    lines.append("")

    for tag, i1, i2, j1, j2 in opcode_ops:
        if tag == "equal":
            a_start = format_address(insts_a[i1].offset)
            a_end = format_address(insts_a[i2 - 1].offset)
            b_start = format_address(insts_b[j1].offset)
            b_end = format_address(insts_b[j2 - 1].offset)
            count = i2 - i1
            lines.append(
                f"  == {a_start}-{a_end} / {b_start}-{b_end}: "
                f"{count} instructions match"
            )
        elif tag == "replace":
            lines.append(
                f"  ~~ REPLACE {i2 - i1} -> {j2 - j1} instructions:"
            )
            for k in range(i1, i2):
                inst = insts_a[k]
                lines.append(
                    f"     {label_a} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )
            for k in range(j1, j2):
                inst = insts_b[k]
                lines.append(
                    f"     {label_b} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )
        elif tag == "delete":
            lines.append(f"  -- DELETE {i2 - i1} instructions from {label_a}:")
            for k in range(i1, i2):
                inst = insts_a[k]
                lines.append(
                    f"     {label_a} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )
        elif tag == "insert":
            lines.append(f"  ++ INSERT {j2 - j1} instructions in {label_b}:")
            for k in range(j1, j2):
                inst = insts_b[k]
                lines.append(
                    f"     {label_b} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )

    lines.append("")

    lines.append("3. INSTRUCTION DIFF MAP (opcode + operands)")
    lines.append("")

    inst_ops = inst_matcher.get_opcodes()
    for tag, i1, i2, j1, j2 in inst_ops:
        if tag == "equal":
            a_start = format_address(insts_a[i1].offset)
            a_end = format_address(insts_a[i2 - 1].offset)
            b_start = format_address(insts_b[j1].offset)
            b_end = format_address(insts_b[j2 - 1].offset)
            count = i2 - i1
            byte_count_a = sum(insts_a[k].length for k in range(i1, i2))
            lines.append(
                f"  == {a_start}-{a_end} / {b_start}-{b_end}: "
                f"{count} instructions ({byte_count_a} bytes)"
            )
        elif tag == "replace":
            lines.append(
                f"  ~~ REPLACE {i2 - i1} -> {j2 - j1} instructions:"
            )
            for k in range(i1, i2):
                inst = insts_a[k]
                lines.append(
                    f"     {label_a} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )
            for k in range(j1, j2):
                inst = insts_b[k]
                lines.append(
                    f"     {label_b} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )
        elif tag == "delete":
            lines.append(f"  -- DELETE {i2 - i1} instructions from {label_a}:")
            for k in range(i1, i2):
                inst = insts_a[k]
                lines.append(
                    f"     {label_a} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )
        elif tag == "insert":
            lines.append(f"  ++ INSERT {j2 - j1} instructions in {label_b}:")
            for k in range(j1, j2):
                inst = insts_b[k]
                lines.append(
                    f"     {label_b} {format_address(inst.offset)}: "
                    f"{format_instruction(inst)}"
                )

    return "\n".join(lines)


# ============================================================
# Entry point
# ============================================================


def compare(version_dirpath_a, version_a, version_dirpath_b, version_b):
    """Compare two ROM versions and print the report.

    Returns 0 on success, 1 on error.
    """
    from disasm_tools.paths import rom_prefix
    pfx_a = rom_prefix(version_dirpath_a)
    pfx_b = rom_prefix(version_dirpath_b)
    rom_filepath_a = version_dirpath_a / "rom" / f"{pfx_a}-{version_a}.rom"
    rom_filepath_b = version_dirpath_b / "rom" / f"{pfx_b}-{version_b}.rom"

    for filepath in (rom_filepath_a, rom_filepath_b):
        if not filepath.exists():
            print(f"Error: ROM file not found: {filepath}", file=sys.stderr)
            return 1

    data_a = rom_filepath_a.read_bytes()
    data_b = rom_filepath_b.read_bytes()

    report = compare_roms(data_a, data_b, version_a, version_b)
    print(report)
    return 0
