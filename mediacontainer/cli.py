"""
# MediaContainer — CLI Entry Point

## Calling API
- `main(argv: list[str] | None = None) -> None`: Entry point for the MediaContainer CLI.

## Algorithmic Methodology
- Parses command line arguments using `argparse`.
- Orchestrates the scanning, grouping, and (future) extraction phases.
- Provides a human-readable summary of identified media containers.
- **Composition Root**: Injects concrete dependencies (Settings, SyslogLogger) into decoupled libraries.

## Program Flow
1. Parse arguments (directory, dry-run).
2. Initialize SyslogLogger and Settings.
3. Resolve the target directory.
4. Invoke `MediaContainer.from_paths` with injected logger and settings.
5. Display a structured list of containers and their contents.
6. (Planned) Trigger extraction.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sysloglogger
from managedsettings import Settings
from .media_container import MediaContainer


def display_containers(media_containers: list[MediaContainer], label: str, verbosity: int, dry_run: bool) -> None:
    """Display the identified media containers in a structured format."""
    if not media_containers:
        if verbosity == 0:
            print(f"[{label}] No media containers found.\n")
        return

    if verbosity == 0:
        print(f"Found {len(media_containers)} media container(s) for '{label}':\n")

    for i, mc in enumerate(media_containers, 1):
        if verbosity > 0:
            # Strict Object Dump Format
            print(f"{mc.name}")

            # 1. Collect Metadata Attributes (Singles)
            # Start with stem as requested
            singles_dict = {
                "scrambled": mc.scrambled,
                "unaffiliated": mc.unaffiliated,
                "incomplete": mc.incomplete,
                "needs_extraction": mc.needs_extraction,
                "extraction_tool": mc.extraction_tool,
            }
            pa = mc.primary_archive
            singles_dict["primary_archive"] = f"'{pa.path.name}'" if pa else None

            # 2. Collect Content (Single-Value or List depending on verbosity)
            content_lists = [
                ("video", mc.video),
                ("sample", mc.sample),
                ("gallery", mc.gallery),
                ("archives", mc.archives),
                ("split_media", mc.split_media),
                ("artwork", mc.artwork),
                ("par_files", mc.par_files),
                ("text_files", mc.text_files),
                ("nzb", mc.nzb),
                ("misc", mc.misc),
            ]

            lists_to_print = []
            for list_name, files in content_lists:
                if not files:
                    continue

                if list_name == "gallery" and verbosity < 2:
                    # Gallery is a "single" in -v mode, but we use bracketed format
                    patterns = set()
                    for f in files:
                        p = f.path.name
                        if f.sequence:
                            p = p.replace(f.sequence, "#" * len(f.sequence), 1)
                        patterns.add(p)
                    
                    for idx, p in enumerate(sorted(patterns)):
                        key = "gallery" if idx == 0 else f"gallery_{idx}"
                        singles_dict[key] = f"[ '{p}' ]"
                else:
                    # Other populated lists are "lists"
                    lists_to_print.append((list_name, files))

            # 3. Print Stem First
            print(f"  stem: '{mc.stem}'")

            # 4. Print other singles in lexical order
            for k in sorted(singles_dict.keys()):
                print(f"  {k}: {singles_dict[k]}")

            # 5. Print Lists
            for list_name, files in lists_to_print:
                print(f"  {list_name} [")
                for f in files:
                    print(f"    '{f.path.name}'")
                print("  ]")
            print()
        else:
            # Standard Summary
            print(f"  [{i}] {mc.name}")

            # Show gallery concisely
            if mc.gallery:
                patterns = set()
                for f in mc.gallery:
                    p = f.path.name
                    if f.sequence:
                        p = p.replace(f.sequence, "#" * len(f.sequence), 1)
                    patterns.add(p)
                for p in sorted(patterns):
                    print(f"      gallery: {p}")

            # Show other files
            for f in mc.files:
                if f.file_type.name == "GALLERY":
                    continue # Handled above

                marker = "  "
                if f.file_type.name in ("ARCHIVE", "MULTIPART_ARCHIVE"):
                    marker = "📦"
                elif f.file_type.name == "VIDEO":
                    marker = "🎬"
                elif f.file_type.name == "IMAGE":
                    marker = "🖼 "
                elif f.file_type.name in ("PAR", "PAR2"):
                    marker = "🔧"
                print(f"      {marker} {f.path.name}  ({f.file_type.name.lower()})")

            if mc.needs_extraction:
                print(f"      → needs extraction ({mc.extraction_tool})")
            print()

    if dry_run:
        print("(dry run — no actions taken)\n")

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mediacontainer",
        description="Identify, group, extract, and play media objects from directories, files, or stdin.",
    )
    parser.add_argument(
        "inputs",
        type=str,
        nargs="*",
        help="Directories to scan, files containing path lists (e.g. .dir, .txt), or '-' for stdin.",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without extracting or playing",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Show detailed dump of media containers. Use -vv for full file lists.",
    )

    # Initialize Global Logger (Composition Root)
    logger = sysloglogger

    try:
        args = parser.parse_args(argv)

        # Determine inputs, defaulting to CWD if none and terminal is interactive
        inputs = args.inputs
        if not inputs:
            if sys.stdin.isatty():
                inputs = ["."]
            else:
                inputs = ["-"]

        # Initialize Global Settings with injected logger
        settings = Settings(path="~/.mediacontainer.json", logger=logger)

        for input_str in inputs:
            paths: list[Path] = []
            label = input_str

            if input_str == "-":
                label = "stdin"
                paths = [Path(line.strip()) for line in sys.stdin if line.strip()]
            else:
                p = Path(input_str)
                if p.is_dir():
                    label = p.resolve().name
                    paths = sorted(f for f in p.iterdir() if f.is_file())
                elif p.is_file():
                    # If it's a known list extension, read lines as paths
                    if p.suffix.lower() in (".dir", ".txt", ".lst", ".filelist"):
                        paths = [Path(line.strip()) for line in p.read_text().splitlines() if line.strip()]
                    else:
                        paths = [p]
                else:
                    # Treat as a single path even if it doesn't exist on disk (for virtual grouping tests)
                    paths = [p]

            if not paths:
                print(f"[{label}] No files found.\n")
                continue

            # Group with injected dependencies
            media_containers = MediaContainer.from_paths(paths, settings=settings, logger=logger)

            display_containers(media_containers, label, args.verbose, args.dry_run)
        # TODO: extraction phase (only if not dry-run and containers found)
        # For now, we just print the same placeholder as before if we reached here
        # print("(extraction not yet implemented)")

    except Exception as e:
        logger.log_error("mediacontainer", f"Unhandled CLI exception: {e}")
        print(f"A critical error occurred. See system logs for details. ({e})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
