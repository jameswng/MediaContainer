"""Tests for file grouping into MediaObjects."""

import tempfile
from pathlib import Path

from m5.grouper import group_files


def _make_dir(filenames: list[str]) -> Path:
    """Create a temp dir with empty files of the given names."""
    d = tempfile.mkdtemp()
    for name in filenames:
        (Path(d) / name).touch()
    return Path(d)


def test_single_archive_group():
    d = _make_dir([
        "Cool.Release-GRP.rar",
        "Cool.Release-GRP.r00",
        "Cool.Release-GRP.r01",
        "Cool.Release-GRP.nfo",
        "Cool.Release-GRP.par2",
        "Cool.Release-GRP.vol0+1.par2",
        "front.jpg",
    ])
    groups = group_files(d)
    assert len(groups) == 1
    assert len(groups[0].files) == 7
    assert groups[0].needs_extraction


def test_single_video_no_extraction():
    d = _make_dir([
        "movie.mkv",
        "movie.srt",
        "movie.nfo",
    ])
    groups = group_files(d)
    assert len(groups) == 1
    assert not groups[0].needs_extraction


def test_two_distinct_archives():
    d = _make_dir([
        "Release.A-GRP.rar",
        "Release.A-GRP.r00",
        "Release.B-GRP.rar",
        "Release.B-GRP.r00",
    ])
    groups = group_files(d)
    assert len(groups) == 2


def test_video_plus_archive_separate():
    d = _make_dir([
        "standalone.movie.mkv",
        "archive.release.rar",
        "archive.release.r00",
    ])
    groups = group_files(d)
    assert len(groups) == 2
