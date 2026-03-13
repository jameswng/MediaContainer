"""
# MediaContainer — Regression Tests

## Calling API
- `pytest tests/test_regression.py`: Execute regression tests against file listing
  fixtures in `tests/fixtures/`.

## Algorithmic Methodology
- **Fixture-based Testing**: Reads `.dir` files containing lists of filenames.
- **Expectation Matching**: Compares identified containers and their attributes
  against the `EXPECTATIONS` dictionary.

## Program Flow
1. Load fixtures from `tests/fixtures/`.
2. For each fixture, convert filenames to `Path` objects.
3. Invoke `MediaContainer.from_paths`.
4. Validate that the number of containers and their specific attributes match `EXPECTATIONS`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from mediacontainer.media_container import MediaContainer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@dataclass
class Expected:
    """Expected outcome for a regression fixture."""
    container_count: int
    # Per-container expectations (indexed by order returned).
    # Each entry is a dict of attribute name → expected value.
    # Only specified attributes are checked.
    containers: list[dict] | None = None


# ---------------------------------------------------------------------------
# Define expected results for each fixture
# ---------------------------------------------------------------------------

import os

...

EXPECTATIONS: dict[str, Expected] = {
    "ambiguous_lena": Expected(
        container_count=2 if os.uname().sysname == "Darwin" else 1,
        # On Mac, 1, 01, 001, (1) are Lena; 2 is Baboon. 
        # Without visual, they all map to numeric stems and might stay in 1 (if unaffiliated) or 2.
    ),
    "stem_mess": Expected(
        container_count=2 if os.uname().sysname == "Darwin" else 1,
        # On Mac, stem-1, stem-01 (Lena) vs stem-10, stem-11 (Baboon)
    ),
    "single_rar_release": Expected(
        container_count=1,
        containers=[{
            "file_count": 12,
            "has_archives": True,
            "has_par": True,
            "has_artwork": True,
            "has_text": True,
            "primary_archive_name": "Cool.Release-GRP.rar",
            "extraction_tool": "unrar",
            "scrambled": False,
            "incomplete": False,
        }],
    ),
    "single_video": Expected(
        container_count=1,
        containers=[{
            "file_count": 3,
            "has_video": True,
            "has_archives": False,
            "has_text": True,
        }],
    ),
    "video_with_sample": Expected(
        container_count=1,
        containers=[{
            "has_video": True,
            "has_sample": True,
            "has_artwork": True,
            "has_text": True,
            "has_archives": False,
        }],
    ),
    "two_distinct_releases": Expected(
        container_count=2,
    ),
    "image_set": Expected(
        container_count=1,
        containers=[{
            "file_count": 13,
            "has_gallery": True,
        }],
    ),
    "split_media": Expected(
        container_count=1,
        containers=[{
            "has_split_media": True,
            "has_text": True,
            "has_archives": False,
        }],
    ),
    "split_archive": Expected(
        container_count=1,
        containers=[{
            "has_archives": True,
            "has_text": True,
            "has_nzb": True,
        }],
    ),
    "multipart_rar": Expected(
        container_count=1,
        containers=[{
            "has_archives": True,
            "has_par": True,
            "has_text": True,
            "extraction_tool": "unrar",
        }],
    ),
    "scrambled_filenames": Expected(
        container_count=1,
        containers=[{
            "scrambled": True,
            "has_archives": True,
        }],
    ),
    "mixed_video_and_archive": Expected(
        container_count=1,
        containers=[{
            "has_video": True,
            "has_archives": True,
            "has_artwork": True,
            "has_text": True,
        }],
    ),
    "par2_only": Expected(
        container_count=1,
        containers=[{
            "has_archives": True,
            "has_par": True,
            "extraction_tool": "unrar",
        }],
    ),
    "single_zip": Expected(
        container_count=1,
        containers=[{
            "has_archives": True,
            "primary_archive_name": "photos.zip",
        }],
    ),
    "seven_z_multipart": Expected(
        container_count=1,
        containers=[{
            "has_archives": True,
            "has_text": True,
            "extraction_tool": "7z",
        }],
    ),
    "empty": Expected(
        container_count=0,
    ),
    "unaffiliated_misc": Expected(
        container_count=1,
        containers=[{
            "unaffiliated": True,
            "file_count": 3,
        }],
    ),
    "multiple_episodes": Expected(
        container_count=2,
        containers=[
            {
                "file_count": 4,
                "has_archives": True,
                "scrambled": False,
                "unaffiliated": False,
            },
            {
                "file_count": 4,
                "has_archives": True,
                "scrambled": False,
                "unaffiliated": False,
            }
        ]
    ),
    "mixed_scrambled_and_clear": Expected(
        container_count=2,
        containers=[
            {
                "file_count": 5,
                "has_archives": True,
                "scrambled": False,
            },
            {
                "file_count": 3,
                "has_archives": True,
                "scrambled": True,
            }
        ]
    ),
    "ambiguous_splits": Expected(
        container_count=3,
        containers=[
            {
                "file_count": 4,
                "has_split_media": True,
                "has_archives": False,
                "has_artwork": True,
            },
            {
                "file_count": 2,
                "has_archives": True,
                "has_split_media": False,
            },
            {
                "file_count": 2,
                "has_archives": True,
            }
        ]
    ),
    "complex_multipart_split": Expected(
        container_count=1,
        containers=[
            {
                "file_count": 7,
                "has_archives": True,
                "has_sample": True,
                "has_artwork": True,
                "has_text": True,
                "primary_archive_name": "Complex.Release.part1.rar.001",
            }
        ]
    ),
    "multiple_qualifiers": Expected(
        container_count=1,
        containers=[{
            "file_count": 4,
            "has_video": True,
            "has_sample": True,
            "has_artwork": True,
        }],
    ),
    "tv_show_season": Expected(
        container_count=1,
        containers=[{
            "file_count": 3,
            "has_video": True,
        }],
    ),
    "multi_version_movie": Expected(
        container_count=2,
        containers=[
            {"file_count": 1, "has_video": True},
            {"file_count": 1, "has_video": True},
        ],
    ),
    "complex_dots_underscores": Expected(
        container_count=1,
        containers=[{
            "file_count": 2,
            "has_video": True,
            "has_text": True,
        }],
    ),
    "case_sensitivity": Expected(
        container_count=1,
        containers=[{
            "file_count": 3,
            "has_video": True,
            "has_text": True,
        }],
    ),
    "non_standard_archive": Expected(
        container_count=1,
        containers=[{
            "file_count": 2,
            "has_archives": True,
        }],
    ),
    "many_accessories": Expected(
        container_count=1,
        containers=[
            {"file_count": 6, "has_video": True, "has_artwork": True},
        ],
    ),
    "near_duplicates": Expected(
        container_count=1,
        containers=[{
            "file_count": 2,
            "has_video": True,
        }],
    ),
    "subtitles_set": Expected(
        container_count=1,
        containers=[{
            "file_count": 4,
            "has_video": True,
        }],
    ),
    "mixed_archives_types": Expected(
        container_count=1,
        containers=[{
            "file_count": 3,
            "has_archives": True,
        }],
    ),
    "misleading_extensions": Expected(
        container_count=2,
        containers=[
            {"file_count": 1, "has_artwork": True},
            {"file_count": 1, "has_text": True},
        ],
    ),
    "very_long_filenames": Expected(
        container_count=1,
        containers=[{
            "file_count": 2,
            "has_video": True,
            "has_text": True,
        }],
    ),
    "numeric_stems": Expected(
        container_count=2,
        containers=[
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 1, "has_video": True},
        ],
    ),
    "dashed_stems": Expected(
        container_count=2,
        containers=[
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 1, "has_video": True},
        ],
    ),
    "multipart_par2_complex": Expected(
        container_count=1,
        containers=[{
            "file_count": 6,
            "has_archives": True,
            "has_par": True,
        }],
    ),
    "whitespace_filenames": Expected(
        container_count=3,
        containers=[
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 2, "has_archives": True},
            {"file_count": 1, "has_text": True},
        ],
    ),
    "metacharacter_filenames": Expected(
        container_count=8,
        containers=[
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 1, "has_video": True},
            {"file_count": 1, "has_video": True},
            {"file_count": 1, "has_video": True},
            {"file_count": 1, "has_video": True},
            {"file_count": 1, "has_video": True},
            {"file_count": 1, "has_video": True},
        ],
    ),
    "unicode_filenames": Expected(
        container_count=6,
        containers=[
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 2, "has_video": True, "has_text": True},
            {"file_count": 2, "has_video": True},
            {"file_count": 2, "has_archives": True, "has_par": True},
            {"file_count": 2, "has_artwork": True},
        ],
    ),
    "minimal_image_stems": Expected(
        container_count=5 if os.uname().sysname == "Darwin" else 3, 
    ),
    "mid_string_sequence": Expected(
        container_count=1,
        containers=[{
            "name": "Holiday_Paris_Eiffel",
            "has_gallery": True,
            "has_text": True,
        }],
    ),
    "bracketed_index": Expected(
        container_count=1,
        containers=[{
            "name": "Vacation",
            "has_gallery": True,
            "has_text": True,
        }],
    ),
    "dominant_separator": Expected(
        container_count=1,
        containers=[{
            "name": "My_Cool_Release",
            "has_gallery": True,
            "has_text": True,
        }],
    ),
    "mixed_separators": Expected(
        container_count=1,
        containers=[{
            "name": "Project.Name.Task",
            "has_gallery": True,
            "has_text": True,
        }],
    ),
    "bracketed_gallery": Expected(
        container_count=1,
        containers=[{
            "name": "stem",
            "has_gallery": True,
        }],
    ),
    "lena_pictorial": Expected(
        container_count=3,
        # Stems: lena, lena_crop, lena_full. 
        # These are NOT "weak" or "inconsistent" (no sequence mess), so visual isn't triggered.
    ),
    "lena_variants": Expected(
        container_count=4,
        # Stems: grayscale, low_quality, original, tiny.
        # Strong stems, no visual analysis triggered.
    ),
    "visual_test": Expected(
        container_count=4,
        # Stems: baboon, cameraman, fruits, peppers.
        # Strong stems, no visual analysis triggered.
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dir_fixture(path: Path) -> list[Path]:
    """Load a .dir file and return a list of Paths (filenames only)."""
    lines = path.read_text().splitlines()
    return [
        Path(line.strip("\r\n"))
        for line in lines
        if line.strip("\r\n")
    ]


def load_real_directory(path: Path) -> list[Path]:
    """Load all files from an actual directory."""
    return sorted(f for f in path.iterdir() if f.is_file())


def check_container(container: MediaContainer, expected: dict) -> None:
    """Assert expected attributes on a MediaContainer."""
    for attr, value in expected.items():
        if attr == "name":
            assert container.name == value, f"Expected name '{value}', got '{container.name}'"
        elif attr == "file_count":
            assert len(container.files) == value, (
                f"Expected {value} files, got {len(container.files)}"
            )
        elif attr == "has_archives":
            assert bool(container.archives) == value
        elif attr == "has_video":
            assert bool(container.video) == value
        elif attr == "has_sample":
            assert bool(container.sample) == value
        elif attr == "has_gallery":
            assert bool(container.gallery) == value
        elif attr == "has_artwork":
            assert bool(container.artwork) == value
        elif attr == "has_par":
            assert bool(container.par_files) == value
        elif attr == "has_text":
            assert bool(container.text_files) == value
        elif attr == "has_nzb":
            assert bool(container.nzb) == value
        elif attr == "has_split_media":
            assert bool(container.split_media) == value
        elif attr == "primary_archive_name":
            assert container.primary_archive is not None, "Expected a primary archive"
            assert container.primary_archive.path.name == value
        elif attr == "extraction_tool":
            assert container.extraction_tool == value
        elif attr == "scrambled":
            assert container.scrambled == value
        elif attr == "incomplete":
            assert container.incomplete == value
        elif attr == "unaffiliated":
            assert container.unaffiliated == value
        else:
            raise ValueError(f"Unknown expected attribute: {attr}")


# ---------------------------------------------------------------------------
# Collect fixtures
# ---------------------------------------------------------------------------

def collect_fixtures() -> list[tuple[str, Path]]:
    """Find all .dir files and directories in fixtures/."""
    fixtures = []
    if FIXTURES_DIR.exists():
        for p in sorted(FIXTURES_DIR.iterdir()):
            if p.suffix == ".dir":
                fixtures.append((p.stem, p))
            elif p.is_dir() and not p.name.startswith("."):
                fixtures.append((p.name, p))
    return fixtures


FIXTURE_IDS = [name for name, _ in collect_fixtures()]
FIXTURE_PATHS = [path for _, path in collect_fixtures()]


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture_name,fixture_path", collect_fixtures(), ids=FIXTURE_IDS)
def test_regression(fixture_name: str, fixture_path: Path):
    """Run a regression test for each fixture."""
    # Load filenames
    if fixture_path.suffix == ".dir":
        paths = load_dir_fixture(fixture_path)
    else:
        paths = load_real_directory(fixture_path)

    # Get expected results
    if fixture_name not in EXPECTATIONS:
        pytest.skip(f"No expectations defined for fixture '{fixture_name}'")

    expected = EXPECTATIONS[fixture_name]

    # Run classification and grouping
    containers = MediaContainer.from_paths(paths)

    # NEW: Verify all input files are accounted for in the containers
    assigned_paths = {f.path for mc in containers for f in mc.files}
    assert len(assigned_paths) == len(paths), (
        f"Input files ({len(paths)}) and assigned files ({len(assigned_paths)}) mismatch. "
        f"Missing: {set(paths) - assigned_paths}"
    )

    # Check container count
    assert len(containers) == expected.container_count, (
        f"Expected {expected.container_count} container(s), "
        f"got {len(containers)}: {[c.name for c in containers]}"
    )

    # Check per-container expectations
    if expected.containers:
        for i, container_expected in enumerate(expected.containers):
            assert i < len(containers), (
                f"Expected at least {i + 1} container(s), got {len(containers)}"
            )
            check_container(containers[i], container_expected)
