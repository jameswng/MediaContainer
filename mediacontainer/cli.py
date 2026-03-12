"""
# MediaContainer — CLI Entry Point

## Calling API
- `main(argv: list[str] | None = None) -> None`: Entry point for the MediaContainer CLI.

## Algorithmic Methodology
- Parses command line arguments using `argparse`.
- Orchestrates the scanning, grouping, and (future) extraction/playback phases.
- Provides a human-readable summary of identified media containers.

## Program Flow
1. Parse arguments (directory, dry-run).
2. Resolve the target directory.
3. Invoke `group_files` to identify media containers.
4. Display a structured list of containers and their contents.
5. (Planned) Trigger extraction and playback.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .media_container import mediacontainer


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mediacontainer",
        description="Identify, group, extract, and play media objects from a directory.",
    )
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without extracting or playing",
    )
    args = parser.parse_args(argv)

    directory: Path = args.directory.resolve()
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    paths = sorted(f for f in directory.iterdir() if f.is_file())
    media_containers = MediaContainer.from_paths(paths)

    if not media_containers:
        print("No files found.")
        sys.exit(0)

    print(f"Found {len(media_containers)} media container(s) in {directory.name}/\n")

    for i, mc in enumerate(media_containers, 1):
        print(f"  [{i}] {mc.name}")
        for f in mc.files:
            marker = "  "
            if f.file_type.name in ("ARCHIVE", "SPLIT_ARCHIVE"):
                marker = "📦"
            elif f.file_type.name == "VIDEO":
                marker = "🎬"
            elif f.file_type.name == "IMAGE":
                marker = "🖼 "
            elif f.file_type.name in ("PAR", "PAR2"):
                marker = "🔧"
            print(f"      {marker} {f.name}  ({f.file_type.name.lower()})")

        if mc.needs_extraction:
            print(f"      → needs extraction")
        print()

    if args.dry_run:
        print("(dry run — no actions taken)")
        return

    # TODO: extraction and playback phases
    print("(extraction and playback not yet implemented)")


if __name__ == "__main__":
    main()
