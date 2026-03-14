# CLAUDE.md

This file provides guidance when working with code in this repository.

## Project overview

Annotated disassembly of the Acorn 6502 Tube Client ROM — the operating system for the 65C02 second (parasite) processor used with the BBC Micro. Python scripts drive py8dis (a programmable 6502 disassembler) to produce readable, verified assembly output from the original ROM binary. The first version covered is 1.10.

## Build commands

Requires [uv](https://docs.astral.sh/uv/) and [beebasm](https://github.com/stardot/beebasm) (v1.10+).

```sh
uv sync                                              # Install dependencies
uv run acorn-tube-client-disasm-tool disassemble 1.10 # Generate .asm and .json from ROM
uv run acorn-tube-client-disasm-tool lint 1.10        # Validate annotation addresses
uv run acorn-tube-client-disasm-tool verify 1.10      # Reassemble and byte-compare against original ROM
```

Verification is the primary correctness check: the generated assembly must reassemble to a byte-identical copy of the original ROM. Lint validates that all annotation addresses (comments, subroutines, labels) reference valid item addresses in the py8dis output. CI runs `disassemble`, `lint`, then `verify` on every push.

## Architecture

### CLI entry point

`src/disasm_tools/cli.py` — subcommands: `disassemble`, `verify`, `lint`, `compare`, `extract`, `audit`, `cfg`, `context`, `labels`, `rename-labels`, `insert-point`, `comment-check`. Sets env vars `ACORN_TUBE_CLIENT_ROM` and `ACORN_TUBE_CLIENT_OUTPUT` before invoking version-specific scripts.

### Disassembly driver

`versions/tube-6502-client-1.10/disassemble/disasm_tube_6502_client_110.py` — the main annotation file. Configures py8dis with labels, constants, subroutine descriptions, comments, and relocated code blocks using py8dis's DSL (`label()`, `constant()`, `comment()`, `subroutine()`, `move()`, `hook_subroutine()`). This is where most development work happens.

### Lint

`src/disasm_tools/lint.py` — validates that every `comment()`, `subroutine()`, and `label()` address in a driver script corresponds to a valid address in the py8dis JSON output. Also validates `address_links` and `glossary_links` in each version's `rom.json`.

### Verification

`src/disasm_tools/verify.py` — assembles the generated `.asm` with beebasm and does a byte-for-byte comparison against the original ROM.

### Version layout

Each ROM version lives under `versions/tube-6502-client-<version>/`. Subdirectories:
- `rom/` — original ROM binary and metadata (`rom.json` with hashes)
- `disassemble/` — py8dis driver script
- `output/` — generated assembly (`.asm`) and structured data (`.json`)

Version IDs in `acornaeology.json` and CLI arguments are bare numbers (`1.10`). The `resolve_version_dirpath()` helper in `src/disasm_tools/paths.py` maps them to the directory using the `tube-6502-client` prefix.

### Glossary

`GLOSSARY.md` — project-level glossary of Tube-specific and Acorn terms, registered in `acornaeology.json` as `"glossary": "GLOSSARY.md"`. Uses Markdown definition-list syntax.

### Disassembly guide

`DISASSEMBLY.md` — development guide covering the workflow for producing version disassemblies, CLI tool reference, py8dis DSL conventions, annotation guidelines, and common gotchas.

## Key technical context

- Tube Client ROM size: 2048 bytes (2 kB, half of a 4 kB ROM)
- ROM base address: TBC (provisionally &F800, occupying &F800-&FFFF)
- The ROM provides the MOS API for the parasite processor by forwarding calls to the host over the Tube interface
- py8dis dependency is a custom fork at `github.com/acornaeology/py8dis`
- Assembly output targets beebasm syntax
- Assembly comments are formatted to fit within 62 characters
- The 65C02 has additional instructions over the NMOS 6502; use "65C02" CPU mode in py8dis
