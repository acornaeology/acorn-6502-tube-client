# Acorn 6502 Tube Client

[![Verify disassembly](https://github.com/acornaeology/acorn-6502-tube-client/actions/workflows/verify.yml/badge.svg)](https://github.com/acornaeology/acorn-6502-tube-client/actions/workflows/verify.yml)

Tube Host client ROM for the 65C02 second (parasite) processor used with the BBC Micro.

This repository contains annotated disassemblies of the Acorn 6502 Tube Client ROM, produced by reverse-engineering the original 65C02 machine code. Each disassembly includes named labels, comments explaining the logic, and cross-references between subroutines.

## Versions

- **Acorn 6502 Tube Client 1.10**
  - [Formatted disassembly on acornaeology.uk](https://acornaeology.uk/acorn-6502-tube-client/1.10.html)
  - [Raw assembly source](versions/tube-6502-client-1.10/output/tube-6502-client-1.10.asm)
  - [Acorn 6502 Tube Client 1.10 in The BBC Micro ROM Library](https://tobylobster.github.io/rom_library/?md5=8c3b9252ac812c892aa21b9252abf94c)

## How it works

The disassembly is produced by a Python script that drives a custom version of [py8dis](https://github.com/acornaeology/py8dis), a programmable disassembler for 6502 binaries. The script feeds the original ROM image to py8dis along with annotations — entry points, labels, constants, and comments — to produce readable assembly output.

The output is verified by reassembling with [beebasm](https://github.com/stardot/beebasm) and comparing the result byte-for-byte against the original ROM. This round-trip verification runs automatically in CI on every push.

## Building locally

Requires [uv](https://docs.astral.sh/uv/) and [beebasm](https://github.com/stardot/beebasm).

```sh
uv sync
uv run acorn-tube-client-disasm-tool disassemble 1.10
uv run acorn-tube-client-disasm-tool verify 1.10
```

## References

- [Acorn 6502 Tube Client ROM v1.20 source code](https://github.com/stardot/Acorn6502TubeROM)
  Original source code for the v1.20 ROM. While a different version, its comments and labels provide important guidance in understanding the earlier v1.10 code.

## Credits

- [py8dis](https://github.com/acornaeology/py8dis) by [SteveF](https://github.com/ZornsLemma), forked for use with acornaeology
- [beebasm](https://github.com/stardot/beebasm) by Rich Mayfield and contributors
- [The BBC Micro ROM Library](https://tobylobster.github.io/rom_library/) by tobylobster

## License

The annotations and disassembly scripts in this repository are released under the [MIT License](LICENSE). The original ROM images remain the property of their respective copyright holders.
