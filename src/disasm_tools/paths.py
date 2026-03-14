"""Shared path resolution for version directories."""

import sys
from pathlib import Path

PREFIX = "tube-6502-client"


def resolve_version_dirpath(versions_dirpath, version_id):
    """Map a version ID to its directory.

    Looks for {PREFIX}-{version_id} under the versions directory.
    Raises SystemExit if no matching directory is found.
    """
    dirpath = versions_dirpath / f"{PREFIX}-{version_id}"
    if dirpath.is_dir():
        return dirpath
    available = sorted(
        p.name for p in versions_dirpath.iterdir() if p.is_dir()
    )
    print(f"Error: version '{version_id}' not found.", file=sys.stderr)
    if available:
        print(f"Available: {', '.join(available)}", file=sys.stderr)
    sys.exit(1)


def rom_prefix(version_dirpath):
    """Extract ROM prefix from a version directory name."""
    # Returns everything before the last hyphen-separated version component.
    # For "tube-6502-client-1.10", returns "tube-6502-client".
    name = version_dirpath.name
    # Find the version suffix by splitting on the prefix
    if name.startswith(PREFIX + "-"):
        return PREFIX
    # Fallback: split on last hyphen group that looks like a version
    return name.rsplit("-", 1)[0]
