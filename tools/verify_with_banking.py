#!/usr/bin/env python3
"""Round-trip verify the Tube Client disassembly with ROM-banking.

The Tube Client ROM file is 4 kB but only the upper 2 kB is mapped at
&F800-&FFFF on the 65C02. ``fantasm verify`` does a strict
byte-for-byte comparison and flags the size mismatch, so this wrapper
slices the upper half into a temp file and feeds that to fantasm's
verify_round_trip API instead.

Drop this script and switch CI back to ``fantasm verify <VER>`` once
fantasm#1 (https://github.com/acornaeology/fantasm/issues/1) lands.

Usage:
    uv run tools/verify_with_banking.py <VERSION_ID>
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from fantasm.api.verify import BeebasmNotFoundError, verify_round_trip
from fantasm.cli_helpers import resolve_version_files
from fantasm.config import resolve_project_context


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <VERSION_ID>", file=sys.stderr)
        return 2
    version_id = argv[1]

    project_context = resolve_project_context(None)
    if not project_context.has_root:
        print("error: not inside a fantasm project", file=sys.stderr)
        return 2
    files = resolve_version_files(project_context, version_id)

    if not files.rom_filepath.exists():
        print(f"error: ROM not found: {files.rom_filepath}", file=sys.stderr)
        return 1
    if not files.asm_filepath.exists():
        print(
            f"error: ASM not found: {files.asm_filepath}\n"
            "       run the driver script first",
            file=sys.stderr,
        )
        return 1

    full_rom = files.rom_filepath.read_bytes()
    if len(full_rom) <= 2048:
        sliced = full_rom
    else:
        # Upper 2 kB is what's mapped at &F800-&FFFF.
        sliced = full_rom[len(full_rom) - 2048:]

    with tempfile.NamedTemporaryFile(suffix=".rom", delete=False) as tmp:
        tmp.write(sliced)
        sliced_filepath = Path(tmp.name)

    try:
        try:
            result = verify_round_trip(sliced_filepath, files.asm_filepath)
        except BeebasmNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    finally:
        sliced_filepath.unlink(missing_ok=True)

    if result.matched:
        print(f"Verification PASSED: {result.rom_size} bytes match (sliced upper 2 kB)")
        return 0

    print(
        f"Verification FAILED: rom={result.rom_size}b "
        f"assembled={result.assembled_size}b "
        + (
            f"first_diff=&{result.first_diff_offset:04X}"
            if result.first_diff_offset is not None
            else "(beebasm error)"
        ),
        file=sys.stderr,
    )
    if result.beebasm_returncode != 0 and result.beebasm_stderr:
        print(result.beebasm_stderr, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
