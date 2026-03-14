#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["jinja2>=3.1"]
# ///
"""Generate README.md from project metadata and a Jinja2 template.

Usage:
    uv run generate_readme.py           # Write README.md
    uv run generate_readme.py --check   # Exit 1 if README.md is out of date
"""

import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

REPO_ROOT = Path(__file__).resolve().parent
REPO_URL = "https://github.com/acornaeology/acorn-6502-tube-client"
SITE_URL = "https://acornaeology.uk"

PREFIX = "tube-6502-client"


def resolve_version_dirpath(versions_dirpath, version_id):
    """Map a version ID to its directory."""
    dirpath = versions_dirpath / f"{PREFIX}-{version_id}"
    if dirpath.is_dir():
        return dirpath
    print(f"Error: version directory not found for '{version_id}'", file=sys.stderr)
    sys.exit(1)


def main():
    manifest = json.loads((REPO_ROOT / "acornaeology.json").read_text())
    slug = manifest["slug"]

    versions = []
    for version_id in manifest["versions"]:
        version_dirpath = resolve_version_dirpath(REPO_ROOT / "versions", version_id)
        version_dirname = version_dirpath.name
        rom_meta = json.loads(
            (version_dirpath / "rom" / "rom.json").read_text()
        )

        docs = []
        for doc in rom_meta.get("docs", []):
            docs.append({
                "label": doc["label"],
                "path": f"versions/{version_dirname}/{doc['path']}",
            })

        versions.append({
            "id": version_id,
            "title": rom_meta.get("title", f"{manifest['name']} {version_id}"),
            "site_url": f"{SITE_URL}/{slug}/{version_id}.html",
            "asm_path": f"{REPO_URL}/blob/master/versions/{version_dirname}/output/{PREFIX}-{version_id}.asm",
            "links": rom_meta.get("links", []),
            "docs": docs,
        })

    env = Environment(
        loader=FileSystemLoader(REPO_ROOT),
        keep_trailing_newline=True,
    )
    template = env.get_template("README.md.j2")

    readme_text = template.render(
        name=manifest["name"],
        description=manifest["description"],
        repo_url=REPO_URL,
        versions=versions,
        references=manifest.get("references", []),
    )

    readme_filepath = REPO_ROOT / "README.md"
    check_mode = "--check" in sys.argv[1:]

    if check_mode:
        if readme_filepath.read_text() != readme_text:
            print(
                "README.md is out of date. "
                "Run 'uv run generate_readme.py' and commit the result.",
                file=sys.stderr,
            )
            sys.exit(1)
        print("README.md is up to date.")
    else:
        readme_filepath.write_text(readme_text)
        print(f"Generated {readme_filepath.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
