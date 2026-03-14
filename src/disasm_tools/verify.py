"""Round-trip assembly verification for Tube Client ROM disassemblies."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def verify(version_dirpath, version):
    """Assemble the disassembly with beebasm and verify it matches the original ROM.

    Returns 0 on success, 1 on failure.
    """
    from disasm_tools.paths import rom_prefix
    prefix = rom_prefix(version_dirpath)
    rom_filepath = version_dirpath / "rom" / f"{prefix}-{version}.rom"
    asm_filepath = version_dirpath / "output" / f"{prefix}-{version}.asm"

    if not rom_filepath.exists():
        print(f"Error: ROM file not found: {rom_filepath}", file=sys.stderr)
        return 1

    if not asm_filepath.exists():
        print(f"Error: assembly file not found: {asm_filepath}", file=sys.stderr)
        print("Run 'acorn-tube-client-disasm-tool disassemble' first.", file=sys.stderr)
        return 1

    beebasm_filepath = shutil.which("beebasm")
    if beebasm_filepath is None:
        print(
            "Error: beebasm not found on PATH.\n"
            "Install beebasm v1.10 or later from https://github.com/stardot/beebasm",
            file=sys.stderr,
        )
        return 1

    full_rom_bytes = rom_filepath.read_bytes()

    # If the ROM file is larger than the assembled output will be,
    # compare against only the trailing portion. The Tube Client ROM
    # is a 4 kB image where only the upper 2 kB is mapped.
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=True) as tmp:
        tmp_filepath = Path(tmp.name)

    result = subprocess.run(
        [beebasm_filepath, "-i", str(asm_filepath), "-o", str(tmp_filepath)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error: beebasm failed (exit code {result.returncode})", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.stdout:
            print(result.stdout, file=sys.stderr, end="")
        return 1

    try:
        assembled_bytes = tmp_filepath.read_bytes()
    except FileNotFoundError:
        print("Error: beebasm did not produce output file", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr, end="")
        return 1
    finally:
        tmp_filepath.unlink(missing_ok=True)

    # Compare against the trailing portion of the ROM if sizes differ
    if len(full_rom_bytes) > len(assembled_bytes):
        offset = len(full_rom_bytes) - len(assembled_bytes)
        rom_bytes = full_rom_bytes[offset:]
    else:
        rom_bytes = full_rom_bytes

    if rom_bytes == assembled_bytes:
        print(
            f"Verification passed: assembled output matches ROM "
            f"({len(rom_bytes)} bytes)"
        )
        return 0

    # Find and report first difference
    min_len = min(len(rom_bytes), len(assembled_bytes))
    first_diff = None
    for i in range(min_len):
        if rom_bytes[i] != assembled_bytes[i]:
            first_diff = i
            break

    if first_diff is None:
        first_diff = min_len

    print("Verification FAILED: assembled output differs from ROM", file=sys.stderr)
    print(f"  ROM size:       {len(rom_bytes)} bytes", file=sys.stderr)
    print(f"  Assembled size: {len(assembled_bytes)} bytes", file=sys.stderr)
    print(f"  First difference at offset ${first_diff:04X}", file=sys.stderr)

    # Show context around the first difference
    context_start = max(0, first_diff - 8)
    context_end = min(min_len, first_diff + 8)

    if first_diff < min_len:
        rom_context = " ".join(f"{b:02X}" for b in rom_bytes[context_start:context_end])
        asm_context = " ".join(
            f"{b:02X}" for b in assembled_bytes[context_start:context_end]
        )
        print(f"  ROM bytes:      {rom_context}", file=sys.stderr)
        print(f"  Assembled:      {asm_context}", file=sys.stderr)

    return 1
