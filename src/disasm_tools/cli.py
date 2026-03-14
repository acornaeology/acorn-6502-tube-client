"""CLI entry point for acorn-tube-client-disasm-tool."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_repo_root():
    """Find the repository root by looking for pyproject.toml."""
    dirpath = Path(__file__).resolve().parent
    while dirpath != dirpath.parent:
        if (dirpath / "pyproject.toml").exists():
            return dirpath
        dirpath = dirpath.parent
    raise RuntimeError("Could not find repository root")


def get_version_dirpath(version):
    """Return the path to a version directory, raising if it doesn't exist."""
    from disasm_tools.paths import resolve_version_dirpath

    repo_root = find_repo_root()
    return resolve_version_dirpath(repo_root / "versions", version)


def rom_prefix(version_dirpath):
    """Return the ROM prefix for a version directory."""
    from disasm_tools.paths import rom_prefix as _rom_prefix

    return _rom_prefix(version_dirpath)


def cmd_disassemble(args):
    """Run the disassembly for a given version."""
    version_dirpath = get_version_dirpath(args.version)
    prefix = rom_prefix(version_dirpath)
    script_filename = f"disasm_{prefix.replace('-', '_')}_{args.version.replace('.', '').lower()}.py"
    script_filepath = version_dirpath / "disassemble" / script_filename

    if not script_filepath.exists():
        print(f"Error: {script_filepath} not found", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env["ACORN_TUBE_CLIENT_ROM"] = str(version_dirpath / "rom" / f"{prefix}-{args.version}.rom")
    env["ACORN_TUBE_CLIENT_OUTPUT"] = str(version_dirpath / "output")

    result = subprocess.run(
        [sys.executable, str(script_filepath)],
        env=env,
    )
    sys.exit(result.returncode)


def cmd_verify(args):
    """Assemble the disassembly and verify it matches the original ROM."""
    from disasm_tools.verify import verify

    version_dirpath = get_version_dirpath(args.version)
    sys.exit(verify(version_dirpath, args.version))


def cmd_lint(args):
    """Validate annotation addresses against the disassembly output."""
    from disasm_tools.lint import lint

    version_dirpath = get_version_dirpath(args.version)
    sys.exit(lint(version_dirpath, args.version))


def cmd_compare(args):
    """Compare two ROM versions byte-by-byte and instruction-by-instruction."""
    from disasm_tools.compare import compare

    version_dirpath_a = get_version_dirpath(args.version_a)
    version_dirpath_b = get_version_dirpath(args.version_b)
    sys.exit(compare(version_dirpath_a, args.version_a,
                     version_dirpath_b, args.version_b))


def cmd_extract(args):
    """Extract a section of disassembly output by address range or label."""
    from disasm_tools.asm_extract import extract

    version_dirpath = get_version_dirpath(args.version)
    prefix = rom_prefix(version_dirpath)
    asm_filepath = version_dirpath / "output" / f"{prefix}-{args.version}.asm"

    if not asm_filepath.exists():
        print(f"Error: {asm_filepath} not found (run disassemble first)", file=sys.stderr)
        sys.exit(1)

    sys.exit(extract(str(asm_filepath), args.start, args.end))


def cmd_audit(args):
    """Audit subroutine annotations."""
    from disasm_tools.audit import audit

    version_dirpath = get_version_dirpath(args.version)
    sys.exit(audit(version_dirpath, args.version,
                   sub_target=args.sub, summary=args.summary,
                   flag_filter=args.flag, undeclared=args.undeclared))


def cmd_insert_point(args):
    """Find insertion point for a new subroutine() declaration."""
    from disasm_tools.insert_point import find_insert_point

    version_dirpath = get_version_dirpath(args.version)
    prefix = rom_prefix(version_dirpath)
    script_filename = f"disasm_{prefix.replace('-', '_')}_{args.version.replace('.', '').lower()}.py"
    driver_filepath = version_dirpath / "disassemble" / script_filename

    if not driver_filepath.exists():
        print(f"Error: {driver_filepath} not found", file=sys.stderr)
        sys.exit(1)

    addr_str = args.address.strip().lstrip("$&").removeprefix("0x")
    try:
        target_addr = int(addr_str, 16)
    except ValueError:
        print(f"Error: invalid address '{args.address}'", file=sys.stderr)
        sys.exit(1)

    sys.exit(find_insert_point(driver_filepath, target_addr))


def cmd_cfg(args):
    """Build and query the inter-procedural call graph."""
    from disasm_tools.cfg import cfg

    version_dirpath = get_version_dirpath(args.version)
    sys.exit(cfg(version_dirpath, args.version,
                 fmt=args.format, leaves=args.leaves, roots=args.roots,
                 sub=args.sub, depth=args.depth))


def cmd_context(args):
    """Generate per-subroutine context files for inline commenting."""
    from disasm_tools.context import generate_context

    version_dirpath = get_version_dirpath(args.version)
    output_dirpath = Path(args.output) if args.output else None
    sys.exit(generate_context(version_dirpath, args.version,
                              threshold=args.threshold,
                              output_dirpath=output_dirpath,
                              single_sub=args.sub,
                              summary_only=args.summary))


def cmd_labels(args):
    """Generate per-label context files for label renaming."""
    from disasm_tools.labels import generate_labels

    version_dirpath = get_version_dirpath(args.version)
    output_dirpath = Path(args.output) if args.output else None
    sys.exit(generate_labels(version_dirpath, args.version,
                             output_dirpath=output_dirpath,
                             category_filter=args.category,
                             single_label=args.label,
                             summary_only=args.summary))


def cmd_comment_check(args):
    """Check inline comments against actual instruction data."""
    from disasm_tools.comment_check import comment_check

    version_dirpath = get_version_dirpath(args.version)
    sys.exit(comment_check(version_dirpath, args.version,
                           sub_target=args.sub, summary=args.summary))


def cmd_rename_labels(args):
    """Batch rename auto-generated labels in a driver script."""
    from disasm_tools.rename_labels import rename_labels, show_sub_labels

    version_dirpath = get_version_dirpath(args.version)

    if args.sub:
        sys.exit(show_sub_labels(version_dirpath, args.version, args.sub))

    if not args.file:
        print("Error: --file or --sub required", file=sys.stderr)
        sys.exit(1)

    renames_filepath = Path(args.file)
    if not renames_filepath.exists():
        print(f"Error: {renames_filepath} not found", file=sys.stderr)
        sys.exit(1)

    renames = []
    for line_num, line in enumerate(renames_filepath.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            print(f"Error: bad format at line {line_num}: {line!r}",
                  file=sys.stderr)
            sys.exit(1)
        addr_str, name = parts
        try:
            addr = int(addr_str.lstrip("$&").removeprefix("0x"), 16)
        except ValueError:
            print(f"Error: bad address at line {line_num}: {addr_str!r}",
                  file=sys.stderr)
            sys.exit(1)
        renames.append((addr, name))

    if not renames:
        print("No renames found in file")
        sys.exit(0)

    prefix = rom_prefix(version_dirpath)
    script_filename = f"disasm_{prefix.replace('-', '_')}_{args.version.replace('.', '').lower()}.py"
    driver_filepath = version_dirpath / "disassemble" / script_filename

    if not driver_filepath.exists():
        print(f"Error: {driver_filepath} not found", file=sys.stderr)
        sys.exit(1)

    sys.exit(rename_labels(driver_filepath, renames))


def main():
    parser = argparse.ArgumentParser(
        prog="acorn-tube-client-disasm-tool",
        description="Acorn 6502 Tube Client ROM disassembly tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dis_parser = subparsers.add_parser(
        "disassemble", help="Run disassembly for a version"
    )
    dis_parser.add_argument("version", help="Version (e.g. 1.10)")
    dis_parser.set_defaults(func=cmd_disassemble)

    verify_parser = subparsers.add_parser(
        "verify", help="Verify disassembly round-trips to original ROM"
    )
    verify_parser.add_argument("version", help="Version (e.g. 1.10)")
    verify_parser.set_defaults(func=cmd_verify)

    lint_parser = subparsers.add_parser(
        "lint", help="Validate annotation addresses in driver script"
    )
    lint_parser.add_argument("version", help="Version (e.g. 1.10)")
    lint_parser.set_defaults(func=cmd_lint)

    compare_parser = subparsers.add_parser(
        "compare", help="Compare two ROM versions"
    )
    compare_parser.add_argument("version_a", help="First version (e.g. 1.10)")
    compare_parser.add_argument("version_b", help="Second version")
    compare_parser.set_defaults(func=cmd_compare)

    extract_parser = subparsers.add_parser(
        "extract", help="Extract assembly section by address or label"
    )
    extract_parser.add_argument("version", help="Version (e.g. 1.10)")
    extract_parser.add_argument("start", help="Start address (hex) or label name")
    extract_parser.add_argument("end", nargs="?", default=None,
                                help="End address (hex) or label name (optional)")
    extract_parser.set_defaults(func=cmd_extract)

    audit_parser = subparsers.add_parser(
        "audit", help="Audit subroutine annotations"
    )
    audit_parser.add_argument("version", help="Version (e.g. 1.10)")
    audit_parser.add_argument("--sub", help="Detail for one subroutine (addr or name)")
    audit_parser.add_argument("--summary", action="store_true",
                              help="Show summary table (default if no --sub)")
    audit_parser.add_argument("--flag", help="Filter summary by flag")
    audit_parser.add_argument("--undeclared", action="store_true",
                              help="List JSR targets without subroutine() declarations")
    audit_parser.set_defaults(func=cmd_audit)

    insert_parser = subparsers.add_parser(
        "insert-point",
        help="Find insertion point for new subroutine() declaration",
    )
    insert_parser.add_argument("version", help="Version (e.g. 1.10)")
    insert_parser.add_argument("address", help="Subroutine address (hex)")
    insert_parser.set_defaults(func=cmd_insert_point)

    cfg_parser = subparsers.add_parser(
        "cfg", help="Build and query inter-procedural call graph"
    )
    cfg_parser.add_argument("version", help="Version (e.g. 1.10)")
    cfg_parser.add_argument("--format", default="json",
                            choices=["json", "dot"],
                            help="Output format (default: json)")
    cfg_parser.add_argument("--leaves", action="store_true",
                            help="List leaf subroutines (no outgoing calls)")
    cfg_parser.add_argument("--roots", action="store_true",
                            help="List root subroutines (no incoming calls)")
    cfg_parser.add_argument("--sub", help="Show callers/callees of a subroutine")
    cfg_parser.add_argument("--depth", action="store_true",
                            help="Show call depth from leaves")
    cfg_parser.set_defaults(func=cmd_cfg)

    context_parser = subparsers.add_parser(
        "context", help="Generate per-subroutine context files for commenting"
    )
    context_parser.add_argument("version", help="Version (e.g. 1.10)")
    context_parser.add_argument("--threshold", type=float, default=50,
                                help="Max comment density %% to include "
                                     "(default: 50)")
    context_parser.add_argument("--output", help="Output directory "
                                "(default: versions/<ver>/context/)")
    context_parser.add_argument("--sub",
                                help="Generate for one subroutine only "
                                     "(addr or name)")
    context_parser.add_argument("--summary", action="store_true",
                                help="Print summary stats only, no files")
    context_parser.set_defaults(func=cmd_context)

    labels_parser = subparsers.add_parser(
        "labels", help="Generate per-label context files for renaming"
    )
    labels_parser.add_argument("version", help="Version (e.g. 1.10)")
    labels_parser.add_argument("--output", help="Output directory "
                               "(default: versions/<ver>/labels/)")
    labels_parser.add_argument("--category",
                               choices=["subroutine", "shared_tail", "data",
                                        "internal_loop",
                                        "internal_conditional"],
                               help="Filter to one category")
    labels_parser.add_argument("--label",
                               help="Generate for one label only "
                                    "(addr or name)")
    labels_parser.add_argument("--summary", action="store_true",
                               help="Print summary stats only, no files")
    labels_parser.set_defaults(func=cmd_labels)

    check_parser = subparsers.add_parser(
        "comment-check", help="Check inline comments against instruction data"
    )
    check_parser.add_argument("version", help="Version (e.g. 1.10)")
    check_parser.add_argument("--sub", help="Check one subroutine only (addr)")
    check_parser.add_argument("--summary", action="store_true",
                              help="Show counts only, no detail")
    check_parser.set_defaults(func=cmd_comment_check)

    rename_parser = subparsers.add_parser(
        "rename-labels", help="Batch rename auto-generated labels"
    )
    rename_parser.add_argument("version", help="Version (e.g. 1.10)")
    rename_parser.add_argument("--file", help="Renames file (addr name per line)")
    rename_parser.add_argument("--sub",
                               help="Show auto-generated labels in a subroutine")
    rename_parser.set_defaults(func=cmd_rename_labels)

    args = parser.parse_args()
    args.func(args)
