"""CLI entry point for m5."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .grouper import group_files


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="m5",
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

    media_objects = group_files(directory)

    if not media_objects:
        print("No files found.")
        sys.exit(0)

    print(f"Found {len(media_objects)} media object(s) in {directory.name}/\n")

    for i, mo in enumerate(media_objects, 1):
        print(f"  [{i}] {mo.name}")
        for f in mo.files:
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

        if mo.needs_extraction:
            print(f"      → needs extraction")
        print()

    if args.dry_run:
        print("(dry run — no actions taken)")
        return

    # TODO: extraction and playback phases
    print("(extraction and playback not yet implemented)")


if __name__ == "__main__":
    main()
