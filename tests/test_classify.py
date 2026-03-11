"""Tests for file classification."""

from pathlib import Path

from m5.classify import FileType, classify


def test_video_detection():
    for ext in (".avi", ".mkv", ".mp4", ".wmv"):
        cf = classify(Path(f"/tmp/movie{ext}"))
        assert cf.file_type == FileType.VIDEO, f"Failed for {ext}"


def test_archive_detection():
    cf = classify(Path("/tmp/release.rar"))
    assert cf.file_type == FileType.ARCHIVE

    cf = classify(Path("/tmp/release.zip"))
    assert cf.file_type == FileType.ARCHIVE


def test_split_archive_detection():
    cf = classify(Path("/tmp/release.r00"))
    assert cf.file_type == FileType.SPLIT_ARCHIVE

    cf = classify(Path("/tmp/release.r99"))
    assert cf.file_type == FileType.SPLIT_ARCHIVE

    cf = classify(Path("/tmp/release.s01"))
    assert cf.file_type == FileType.SPLIT_ARCHIVE

    cf = classify(Path("/tmp/release.001"))
    assert cf.file_type == FileType.SPLIT_ARCHIVE


def test_par2_detection():
    cf = classify(Path("/tmp/release.par2"))
    assert cf.file_type == FileType.PAR2

    cf = classify(Path("/tmp/release.vol0+1.par2"))
    assert cf.file_type == FileType.PAR2


def test_image_detection():
    cf = classify(Path("/tmp/front.jpg"))
    assert cf.file_type == FileType.IMAGE

    cf = classify(Path("/tmp/screen.png"))
    assert cf.file_type == FileType.IMAGE


def test_base_name_normalization():
    cf = classify(Path("/tmp/My.Cool.Release-GRP.rar"))
    assert cf.base_name == "my cool release-grp"

    cf = classify(Path("/tmp/My.Cool.Release-GRP.r00"))
    assert cf.base_name == "my cool release-grp"


def test_par2_base_name_strips_volume():
    cf = classify(Path("/tmp/release.vol0+1.par2"))
    assert cf.base_name == "release"
