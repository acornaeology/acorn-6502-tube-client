# Disassembly Guide

How to produce annotated, verified disassemblies of Acorn 6502 Tube Client ROM versions.

For project overview and build instructions, see [README.md](README.md). For architecture details, see [CLAUDE.md](CLAUDE.md). For terminology, see [GLOSSARY.md](GLOSSARY.md).


## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python dependency management
- [beebasm](https://github.com/stardot/beebasm) (v1.10+) for assembly verification
- The ROM binary (2048 bytes) for the version being disassembled
- MD5 and SHA-256 hashes of the ROM (`md5 <rom>`, `shasum -a 256 <rom>`)


## Quick reference: CLI tools

The disassembly tooling is provided by [fantasm](https://github.com/acornaeology/fantasm), invoked as `uv run fantasm <command>`. The full command surface is documented in fantasm's own README; the most-used commands here are:

| Command | Description | Example |
|---------|-------------|---------|
| (driver script) | Run py8dis to generate `.asm` and `.json` from ROM | `uv run python versions/tube-6502-client-1.10/disassemble/disasm_tube_6502_client_110.py` |
| `tools/verify_with_banking.py` | Slice the upper 2 kB and verify with beebasm | `uv run tools/verify_with_banking.py 1.10` |
| `lint` | Validate annotation addresses against the disassembly | `fantasm lint 1.10 versions/tube-6502-client-1.10/disassemble/disasm_tube_6502_client_110.py` |
| `compare` | Compare two ROM versions (byte and opcode level) | `fantasm compare 1.10 1.20` |
| `asm extract` | Extract assembly section by address range or label | `fantasm asm extract 1.10 &F800 &F900` |
| `audit summary/detail/undeclared` | Subroutine annotation audit | `fantasm audit summary 1.10` |
| `cfg leaves/roots/depth/sub/blocks/sub-context` | Inter-procedural call graph queries | `fantasm cfg depth 1.10` |
| `comments suggest/check` | Comment suggestions and consistency checks | `fantasm comments check 1.10` |
| `labels classify/apply` | Auto-label classification + rename application | `fantasm labels classify 1.10` |
| `sub insert` | Find insertion point for a new `subroutine()` | `fantasm sub insert <driver> &F800` |
| `addresses map` | Map source addresses to a target ROM | `fantasm addresses map 1.10 1.20 --addr 0xF800` |

`fantasm` accepts hex addresses in multiple formats (`&F800`, `$F800`, `0xF800`) as well as label names where appropriate.


## Producing a new version disassembly

### Step 1: Directory structure

Create the version directory tree:

```
versions/tube-6502-client-<VER>/
  rom/
    tube-6502-client-<VER>.rom   # The ROM binary
    rom.json                     # Metadata: title, size, md5, sha256
  disassemble/
    __init__.py                  # Empty
    disasm_tube_6502_client_<ver>.py  # Driver script (dots removed)
  output/                        # Generated .asm and .json go here
```

Update `acornaeology.json` to add the new version to the versions array.


### Step 2: Build the driver script

For the first version, start with a minimal driver that loads the ROM and sets entry points. For subsequent versions, use address mapping from the nearest existing version.


### Step 3: Iterate

Run:

```sh
uv run python versions/tube-6502-client-<VER>/disassemble/disasm_tube_6502_client_<VER_NO_DOTS>.py
uv run tools/verify_with_banking.py <VER>
```

Fix errors until verification passes, then annotate.


## py8dis driver script reference

The driver script configures py8dis using a Python DSL. Each call annotates the disassembly output.

### Core DSL calls

**`label(address, name)`** — Assign a symbolic name to a ROM or RAM address.

**`constant(name, value)`** — Define a named constant for a numeric value. Used for hardware register addresses, OSBYTE numbers, etc. The value is symbolic, not a ROM address.

**`comment(address, text)`** — Attach a comment to a specific instruction address.

**`subroutine(address, title, description)`** — Mark the start of a subroutine with a title and description.

**`entry(address)`** — Mark an address as a code entry point.

**`move(dest, source, length)`** — Declare a relocated code block.

**`hook_subroutine(address, hook_function)`** — Register a custom Python function for special handling.


## Annotation guidelines

### Subroutine descriptions

A good subroutine description:

- **Title**: A standalone phrase or short sentence summarising the routine's purpose.
- **Description**: Explains behaviour, entry/exit conditions, and side effects.
- **Calling convention**: Uses `On entry:` and `On exit:` blocks with indented register/flag details.

### Comment length

Assembly comments are formatted to fit within 62 characters (py8dis formatting constraint).

### Hex notation

- Use **Acorn notation** (`&XXXX`) in documentation, Markdown files, and human-readable output
- Use **Python notation** (`0xXXXX`) in Python scripts (driver scripts, tools)


## Key gotchas

1. **py8dis auto-labels can collide.** Any `return_N`, `loop_cXXXX`, etc. that appears in both main ROM and relocated code will cause beebasm duplicate label errors. Fix by adding explicit labels.

2. **`constant()` doesn't take ROM addresses.** Constants are symbolic values and should NOT have their values transformed by address maps.

3. **The ROM is exactly 2048 bytes.** Much smaller than a standard 8 kB sideways ROM. Code is tightly packed.

4. **Use 65C02 CPU mode.** The parasite processor is a 65C02, which has additional instructions and addressing modes over the NMOS 6502.


## Tools reference

The disassembly toolchain itself lives in [fantasm](https://github.com/acornaeology/fantasm) — see its API/CLI docs for module-level details. The repo-local tools that remain are:

| Tool | Source | Purpose |
|------|--------|---------|
| Verify (banked) | `tools/verify_with_banking.py` | Slice the upper 2 kB out of the 4 kB ROM and verify via `fantasm.api.verify` |
| README generator | `generate_readme.py` | Render `README.md` from `acornaeology.json` and `README.md.j2` |
