#!/usr/bin/env python3
"""
# MediaContainer — Fixture Results Demonstration

## Calling API
- `python3 bin/show_fixture_results.py`: Demonstrates the grouping results for
  various test fixtures.

## Algorithmic Methodology
- Loads filenames from `.dir` fixture files.
- Invokes `MediaContainer.from_paths`.
- Displays identified containers and their categorized contents.

## Program Flow
1. Resolve project root and inject into `sys.path`.
2. Select representative fixtures.
3. For each fixture:
   a. Load filenames.
   b. Group with `MediaContainer`.
   c. Print a structured summary.
"""

import sys
from pathlib import Path

# --- Self-Locating Executable ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mediacontainer.media_container import MediaContainer  # noqa: E402

def load_fixture(name: str) -> list[Path]:
    path = ROOT / "tests" / "fixtures" / f"{name}.dir"
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    return [Path(line.strip()) for line in lines if line.strip() and not line.startswith("#")]

def main():
    fixtures = [
        "single_rar_release",
        "image_set",
        "scrambled_filenames",
        "mixed_video_and_archive"
    ]

    for name in fixtures:
        print(f"=== Fixture: {name} ===")
        paths = load_fixture(name)
        containers = MediaContainer.from_paths(paths)
        
        for i, mc in enumerate(containers, 1):
            print(f"  [{i}] Container Name: '{mc.name}'")
            if mc.scrambled:
                print("      (Scrambled Filenames Detected)")
            if mc.unaffiliated:
                print("      (Unaffiliated Catch-all)")
                
            categories = {
                "🎬 Playable": mc.playable,
                "🎞 Sample": mc.sample,
                "🖼 Artwork": mc.artwork,
                "📦 Archives": mc.archives,
                "🔧 Par2": mc.par_files,
                "✂️ Split": mc.split_media,
                "📄 Text": mc.text_files,
                "🏷 NZB": mc.nzb,
                "❓ Misc": mc.misc
            }
            
            for label, files in categories.items():
                if files:
                    print(f"      {label}: {len(files)} file(s)")
                    # Print first 2 files as examples
                    for f in files[:2]:
                        print(f"        - {f.path.name}")
                    if len(files) > 2:
                        print(f"        - ... (+{len(files)-2} more)")
        print("-" * 40)

if __name__ == "__main__":
    main()
