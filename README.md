# Acorn 6502 Tube Client

[![Verify disassembly](https://github.com/acornaeology/acorn-6502-tube-client/actions/workflows/verify.yml/badge.svg)](https://github.com/acornaeology/acorn-6502-tube-client/actions/workflows/verify.yml)

The Tube Client ROM for the 65C02/65C102 second processors used with the BBC Micro. Two variants of v1.10 were produced: One for the external 3 MHz "cheese-wedge" second processor, and another for the internal 4 MHz board for the Master Turbo. The Tube Client serves as the operating system for the second processor, providing the standard BBC Micro MOS API by forwarding calls over the Tube interface to the host machine. The entire OS fits in just 2 kB, stored in the upper half of a 4 kB ROM device.

This repository contains annotated disassemblies of the Acorn 6502 Tube Client ROM, produced by reverse-engineering the original 65C02 machine code. Each disassembly includes named labels, comments explaining the logic, and cross-references between subroutines.

## Versions

- **Acorn 6502 Tube Client 1.10 (external 65C02 3 MHz)**
  - [Formatted disassembly on acornaeology.uk](https://acornaeology.uk/acorn-6502-tube-client/1.10.html)
  - [Disassembly source on GitHub](https://github.com/acornaeology/acorn-6502-tube-client/blob/master/versions/tube-6502-client-1.10/output/tube-6502-client-1.10.asm)
  - [Acorn 6502 Tube Client 1.10 in The BBC Micro ROM Library](https://tobylobster.github.io/rom_library/?md5=8c3b9252ac812c892aa21b9252abf94c)
  - [Discuss this disassembly on the Stardot Forums thread: Annotated disassembly of Acorn 6502 Tube Client ROM](https://www.stardot.org.uk/forums/viewtopic.php?t=32686)

## How it works

The disassembly is produced by a Python script that drives [dasmos](https://github.com/acornaeology/dasmos), a programmable disassembler for 6502/65C02 binaries with a stable 1.0 API and byte-faithful round-trip oracle. The script feeds the original ROM image to dasmos along with annotations — entry points, labels, constants, and comments — to produce readable assembly output.

The output is verified by reassembling with [beebasm](https://github.com/stardot/beebasm) and comparing the result byte-for-byte against the original ROM. This round-trip verification runs automatically in CI on every push.

The analysis surface around dasmos (verify, lint, audit, cfg, comments, address mapping across versions, …) is provided by [fantasm](https://acornaeology.github.io/fantasm/) — see its docs for the full command and API reference.

## Disassembling locally

Requires [uv](https://docs.astral.sh/uv/) and [beebasm](https://github.com/stardot/beebasm) (v1.10+).

```sh
uv sync
uv run fantasm disassemble 1.10
uv run fantasm verify 1.10
```

## (Re-)Assembling locally

To assemble the `.asm` file back into a ROM image using [beebasm](https://github.com/stardot/beebasm):

```sh
beebasm -i versions/tube-6502-client-1.10/output/tube-6502-client-1.10.asm -o tube-6502-client-1.10.rom
```

## References

- [Original Acorn source code for v1.10 (UADE format)](https://github.com/stardot/Acorn6502TubeROM/blob/master/uadesrc/tube6502.uade)
  The original Acorn source code for the 6502 Tube Client, in UADE (Universal Assembler/Disassembler/Editor) format.
- [J.G. Harston's reassembly of the v1.10 Tube Client (BBC BASIC)](https://web.archive.org/web/20200613192357/http://mdfs.net/Software/Tube/6502/Clnt65v1.src)
  A BBC BASIC reassembly of the 6502 Tube Client ROM.
- [Dave Banks' working disassembly of the v1.10 Client ROM (beebasm)](https://github.com/hoglet67/6502ClientROM)
  A beebasm disassembly including conditional assembly for the Acorn Turbo 256K variant.
- [Tom Seddon's reassembly of the 6502 Tube Client](https://github.com/tom-seddon/acorn_6502_copro_os_disassembly)
  Another reassembly of the 6502 Tube Client ROM.
- [Stardot Forums: Annotated disassembly of Acorn 6502 Tube Client ROM](https://www.stardot.org.uk/forums/viewtopic.php?t=32686)
  Discussion thread for the 6502 Tube Client disassembly.

## Credits

- [dasmos](https://github.com/acornaeology/dasmos) — programmable 6502/65C02 disassembler used to produce the annotated assembly
- [beebasm](https://github.com/stardot/beebasm) by Rich Mayfield and contributors
- [The BBC Micro ROM Library](https://tobylobster.github.io/rom_library/) by tobylobster

## License

The annotations and disassembly scripts in this repository are released under the [MIT License](LICENSE). The original ROM images remain the property of their respective copyright holders.
