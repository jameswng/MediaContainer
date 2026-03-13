"""
# MediaContainer — Fixture Results Visualization Script

## Calling API
- `python3 bin/show_fixture_results.py`: Scan all fixtures and show grouping results.

## Algorithmic Methodology
- Loads each fixture from `tests/fixtures/`.
- Runs `MediaContainer.from_paths()`.
- Prints a structured summary of identified containers and their attributes.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT))

from mediacontainer.media_container import MediaContainer

FIXTURES_DIR = ROOT / "tests" / "fixtures"

def load_fixture(path: Path) -> list[Path]:
    if path.suffix == ".dir":
        return [Path(line.strip()) for line in path.read_text().splitlines() if line.strip()]
    return sorted(f for f in path.iterdir() if f.is_file())

def main():
    fixtures = []
    for p in sorted(FIXTURES_DIR.iterdir()):
        if p.suffix == ".dir":
            fixtures.append(p)
        elif p.is_dir() and not p.name.startswith("."):
            fixtures.append(p)

    for fix in fixtures:
        print(f"\n{'='*80}")
        print(f" FIXTURE: {fix.name}")
        print(f"{'='*80}")
        
        paths = load_fixture(fix)
        containers = MediaContainer.from_paths(paths)
        
        for i, mc in enumerate(containers, 1):
            print(f"  [{i}] {mc.name}")
            print(f"      Attributes: scrambled={mc.scrambled}, unaffiliated={mc.unaffiliated}, incomplete={mc.incomplete}")
            
            categories = {
                "🎬 Video": mc.video,
                "🎞  Gallery": mc.gallery,
                "📦 Archives": mc.archives,
                "🖼  Artwork": mc.artwork,
                "🔧 PAR": mc.par_files,
                "✂️  Split": mc.split_media,
                "📝 Text": mc.text_files,
                "🔗 NZB": mc.nzb,
                "📄 Misc": mc.misc
            }
            
            for label, files in categories.items():
                if files:
                    print(f"      {label}:")
                    for f in files:
                        print(f"        - {f.path.name}")
        
        if not containers:
            print("  (No containers identified)")

if __name__ == "__main__":
    main()
