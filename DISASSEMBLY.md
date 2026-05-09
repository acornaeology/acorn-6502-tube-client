# Disassembly Guide

How to produce annotated, verified disassemblies of Acorn 6502 Tube Client ROM versions.

For project overview and build instructions, see [README.md](README.md). For architecture details, see [CLAUDE.md](CLAUDE.md). For terminology, see [GLOSSARY.md](GLOSSARY.md).


## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python dependency management
- [beebasm](https://github.com/stardot/beebasm) (v1.10+) for assembly verification
- The ROM binary (2048 bytes) for the version being disassembled
- MD5 and SHA-256 hashes of the ROM (`md5 <rom>`, `shasum -a 256 <rom>`)


## Quick reference: CLI tools

The disassembly tooling is provided by [fantasm](https://acornaeology.github.io/fantasm/), invoked as `uv run fantasm <command>`. The full command-by-command reference is at <https://acornaeology.github.io/fantasm/cli.html> and the workflow guide at <https://acornaeology.github.io/fantasm/workflows.html>; the most-used commands here are:

| Command | Description | Example |
|---------|-------------|---------|
| `disassemble` | Run the dasmos driver to generate `.asm` and `.json` from ROM | `fantasm disassemble 1.10` |
| `verify` | Reassemble and byte-compare (slices the upper 2 kB automatically) | `fantasm verify 1.10` |
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
uv run fantasm disassemble <VER>
uv run fantasm verify <VER>
```

Fix errors until verification passes, then annotate.


## dasmos driver script reference

The driver script configures a `dasmos.Disassembler` instance using its Python API. Each call annotates the disassembly output. The full driver-API guide is at <https://acornaeology.github.io/dasmos/driver_api.html>.

### Core API calls

**`d = dasmos.Disassembler.create(cpu="65C02", ...)`** — Construct the disassembler. Use `cpu="65C02"` for the parasite processor.

**`d.load(rom_filepath, base_address)`** — Load a ROM image at a given base address.

**`d.label(address, name)`** — Assign a symbolic name to a ROM or RAM address (covers both in-ROM and runtime-only addresses).

**`d.comment(address, text)`** — Attach a comment to a specific instruction address.

**`d.subroutine(address, title, description)`** — Mark the start of a subroutine with a title and description.

**`d.entry(address, name=...)`** — Mark an address as a code entry point.

**`d.add_move(dest, source, length)`** — Declare a relocated code block; returns a typed `Move` handle that is also a context manager (`with move: d.label(...)` scopes annotations under it).

**`d.hook_subroutine(address, hook_function)`** — Register a custom Python function for special handling. Bundled hooks (`stringhi_hook`, `stringz_hook`, `stringcr_hook`) live in `dasmos.hooks`.

**`d.format_hint(addr, FormatHint.X)`** / sugars `d.char_literal(addr)`, `d.inkey_code(addr)` — Declare the operand-byte's semantic intent (CHAR / DECIMAL / HEX / BINARY / OCTAL / INKEY); each renderer chooses its syntax.

**`ir = d.disassemble()` then `ir.render("beebasm" | "json")`** — Produce the rendered assembly or structured JSON output.


## Annotation guidelines

### Subroutine descriptions

A good subroutine description:

- **Title**: A standalone phrase or short sentence summarising the routine's purpose.
- **Description**: Explains behaviour, entry/exit conditions, and side effects.
- **Calling convention**: Uses `On entry:` and `On exit:` blocks with indented register/flag details.

### Comment length

Assembly comments are formatted to fit within 62 characters (dasmos beebasm-renderer formatting constraint, inherited from py8dis layout conventions).

### Hex notation

- Use **Acorn notation** (`&XXXX`) in documentation, Markdown files, and human-readable output
- Use **Python notation** (`0xXXXX`) in Python scripts (driver scripts, tools)


## Key gotchas

1. **Auto-labels can collide.** Any `return_N`, `loop_cXXXX`, etc. that appears in both main ROM and relocated code will cause beebasm duplicate label errors. Fix by adding explicit labels.

2. **`constant()` doesn't take ROM addresses.** Constants are symbolic values and should NOT have their values transformed by address maps.

3. **The ROM is exactly 2048 bytes.** Much smaller than a standard 8 kB sideways ROM. Code is tightly packed.

4. **Use 65C02 CPU mode.** The parasite processor is a 65C02, which has additional instructions and addressing modes over the NMOS 6502. Pass `cpu="65C02"` to `dasmos.Disassembler.create(...)`.


## Tools reference

The disassembly toolchain itself lives in [fantasm](https://acornaeology.github.io/fantasm/) — see [the published docs](https://acornaeology.github.io/fantasm/) for module-level details. The repo-local tools that remain are:

| Tool | Source | Purpose |
|------|--------|---------|
| README generator | `generate_readme.py` | Render `README.md` from `acornaeology.json` and `README.md.j2` |
