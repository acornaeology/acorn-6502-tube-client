# CLAUDE.md

This file provides guidance when working with code in this repository.

## Project overview

Annotated disassembly of the Acorn 6502 Tube Client ROM — the operating system for the 65C02 second (parasite) processor used with the BBC Micro. Python scripts drive py8dis (a programmable 6502 disassembler) to produce readable, verified assembly output from the original ROM binary. The first version covered is 1.10.

## Build commands

Requires [uv](https://docs.astral.sh/uv/) and [beebasm](https://github.com/stardot/beebasm) (v1.10+).

```sh
uv sync                                                                                              # Install dependencies (incl. fantasm)
uv run fantasm disassemble 1.10                                                                       # Run py8dis driver via fantasm (sets FANTASM_ROM / FANTASM_OUTPUT_DIR)
uv run fantasm lint 1.10 versions/tube-6502-client-1.10/disassemble/disasm_tube_6502_client_110.py   # Validate annotation addresses
uv run fantasm verify 1.10                                                                            # Reassemble and byte-compare (slices the upper 2 kB automatically)
```

Verification is the primary correctness check: the generated assembly must reassemble to a byte-identical copy of the upper 2 kB of the original ROM. Lint validates that all annotation addresses (comments, subroutines, labels) reference valid item addresses in the py8dis output. CI runs disassemble, lint, then verify on every push.

## Architecture

### Tooling: fantasm + py8dis

The disassembly tooling is provided by [fantasm](https://github.com/acornaeology/fantasm) — installed as a regular project dependency. fantasm exposes a `fantasm` CLI (subcommands: `verify`, `lint`, `compare`, `audit`, `cfg`, `comments`, `labels`, `context`, `asm`, `sub`, `addresses`, `annotations`, `backfill`, `promote`, `fingerprint`, `shared`, `info`, `project`) and a `fantasm.api` package for programmatic use. Project layout, prefixes, and per-version metadata live in `fantasm.toml`.

[py8dis](https://github.com/acornaeology/py8dis) (a programmable 6502/65C02 disassembler) is invoked directly via the per-version driver script under `versions/tube-6502-client-<VER>/disassemble/`; fantasm operates on the `.asm` / `.json` artefacts py8dis emits.

### Disassembly driver

`versions/tube-6502-client-1.10/disassemble/disasm_tube_6502_client_110.py` — the main annotation file. Configures py8dis with labels, constants, subroutine descriptions, comments, and relocated code blocks using py8dis's DSL (`label()`, `constant()`, `comment()`, `subroutine()`, `move()`, `hook_subroutine()`). The driver also performs the 4 kB → 2 kB upper-half slice before feeding py8dis. This is where most development work happens.

### Lint

`fantasm lint <VER> <DRIVER_PATH>` validates that every `comment()`, `subroutine()`, and `label()` address in a driver script corresponds to a valid address in the py8dis JSON output. Doc-link checks against `rom.json`'s `address_links` / `glossary_links` aren't covered by fantasm yet; they remain TODO.

### Verification

`fantasm verify <VER>` assembles the generated `.asm` with beebasm and compares it against the original ROM. Tube Client's ROM file is 4 kB but only the upper 2 kB is mapped at &F800-&FFFF; fantasm 0.4.0's verify slices the trailing portion of the file when it's larger than the assembled output, so this comparison Just Works without a project-side wrapper.

### Version layout

Each ROM version lives under `versions/tube-6502-client-<version>/`. Subdirectories:
- `rom/` — original ROM binary and metadata (`rom.json` with hashes)
- `disassemble/` — py8dis driver script
- `output/` — generated assembly (`.asm`) and structured data (`.json`)

Version IDs in `acornaeology.json` and CLI arguments are bare numbers (`1.10`). The directory layout is governed by `[versions] prefixes` in `fantasm.toml`; fantasm's `resolve_version_files()` maps a version ID to the matching `versions/tube-6502-client-{version_id}/` directory.

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
