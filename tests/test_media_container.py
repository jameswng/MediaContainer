"""Unit tests for MediaContainer module."""

from pathlib import Path

import pytest

from mediacontainer.media_container import ClassifiedFile, FileType, MediaContainer



# ---------------------------------------------------------------------------
# Stem extraction
# ---------------------------------------------------------------------------

class TestStemExtraction:
    """Test the iterative peel/strip/normalize algorithm."""

    @pytest.mark.parametrize("filename, expected_stem", [
        # Basic extensions
        ("release.rar", "release"),
        ("release.zip", "release"),
        ("release.7z", "release"),
        ("movie.mkv", "movie"),
        ("movie.avi", "movie"),
        ("movie.mp4", "movie"),
        ("image.jpg", "image"),
        ("info.nfo", "info"),
        ("info.txt", "info"),
        ("file.nzb", "file"),
        # Rar volumes
        ("release.r00", "release"),
        ("release.r99", "release"),
        ("release.s00", "release"),
        # Part notation
        ("release.part1.rar", "release"),
        ("release.part01.rar", "release"),
        ("release.part001.rar", "release"),
        # Numeric splits
        ("release.rar.001", "release"),
        ("release.rar.002", "release"),
        ("movie.avi.001", "movie"),
        ("archive.7z.001", "archive"),
        # Par2 with volumes
        ("release.par2", "release"),
        ("release.vol0+1.par2", "release"),
        ("release.vol000+01.par2", "release"),
        ("release.vol001+02.par2", "release"),
        # Qualifiers stripped
        ("release-sample.avi", "release"),
        ("release_sample.mkv", "release"),
        ("release_screenshot.jpg", "release"),
        ("release-subs.rar", "release"),
        ("release-proof.jpg", "release"),
        ("release-covers.rar", "release"),
        # Dots/underscores normalized to spaces
        ("My.Cool.Release-GRP.rar", "my cool release-grp"),
        ("My_Cool_Release-GRP.r00", "my cool release-grp"),
        # Hyphens preserved
        ("Release-GRP.rar", "release-grp"),
        # Accessory names stay as-is (no qualifier to strip)
        ("front.jpg", "front"),
        ("back.jpg", "back"),
        ("cover.png", "cover"),
        ("screen.jpg", "screen"),
        ("index.jpg", "index"),
    ])
    def test_stem_extraction(self, filename, expected_stem):
        cf = ClassifiedFile.from_filename(filename)
        assert cf.stem == expected_stem


# ---------------------------------------------------------------------------
# File classification
# ---------------------------------------------------------------------------

class TestFileClassification:

    @pytest.mark.parametrize("filename, expected_type", [
        ("movie.avi", FileType.VIDEO),
        ("movie.mkv", FileType.VIDEO),
        ("movie.mp4", FileType.VIDEO),
        ("movie.wmv", FileType.VIDEO),
        ("movie.flv", FileType.VIDEO),
        ("movie.mov", FileType.VIDEO),
        ("movie.ts", FileType.VIDEO),
        ("movie.vob", FileType.VIDEO),
        ("movie.webm", FileType.VIDEO),
        ("image.jpg", FileType.IMAGE),
        ("image.jpeg", FileType.IMAGE),
        ("image.png", FileType.IMAGE),
        ("image.gif", FileType.IMAGE),
        ("image.bmp", FileType.IMAGE),
        ("image.webp", FileType.IMAGE),
        ("archive.rar", FileType.ARCHIVE),
        ("archive.zip", FileType.ARCHIVE),
        ("archive.7z", FileType.ARCHIVE),
        ("archive.r00", FileType.MULTIPART_ARCHIVE),
        ("archive.r99", FileType.MULTIPART_ARCHIVE),
        ("archive.s01", FileType.MULTIPART_ARCHIVE),
        ("release.part1.rar", FileType.MULTIPART_ARCHIVE),
        ("release.part02.rar", FileType.MULTIPART_ARCHIVE),
        ("file.001", FileType.SPLIT_FILE),
        ("file.999", FileType.SPLIT_FILE),
        ("release.par", FileType.PAR),
        ("release.par2", FileType.PAR2),
        ("release.vol0+1.par2", FileType.PAR2),
        ("info.nfo", FileType.TEXT),
        ("readme.txt", FileType.TEXT),
        ("file.nzb", FileType.NZB),
        ("unknown.xyz", FileType.OTHER),
    ])
    def test_file_type_detection(self, filename, expected_type):
        cf = ClassifiedFile.from_filename(filename)
        assert cf.file_type == expected_type


# ---------------------------------------------------------------------------
# Filename anatomy (decomposed parts)
# ---------------------------------------------------------------------------

class TestFilenameAnatomy:

    def test_simple_archive(self):
        cf = ClassifiedFile.from_filename("release.rar")
        assert cf.stem == "release"
        assert cf.extension == ".rar"
        assert cf.qualifier is None
        assert cf.volume is None
        assert cf.split is None

    def test_multipart_with_volume(self):
        cf = ClassifiedFile.from_filename("release.r05")
        assert cf.stem == "release"
        assert cf.volume == ".r05"

    def test_part_notation(self):
        cf = ClassifiedFile.from_filename("release.part3.rar")
        assert cf.stem == "release"
        assert cf.volume == ".part3"
        assert cf.extension == ".rar"

    def test_numeric_split(self):
        cf = ClassifiedFile.from_filename("release.rar.001")
        assert cf.stem == "release"
        assert cf.extension == ".rar"
        assert cf.split == ".001"

    def test_qualifier(self):
        cf = ClassifiedFile.from_filename("release-sample.avi")
        assert cf.stem == "release"
        assert cf.qualifier == "sample"
        assert cf.extension == ".avi"

    def test_par2_volume(self):
        cf = ClassifiedFile.from_filename("release.vol003+04.par2")
        assert cf.stem == "release"
        assert cf.volume == ".vol003+04"
        assert cf.extension == ".par2"

    def test_complex_compound(self):
        cf = ClassifiedFile.from_filename("My.Release-GRP-sample.part1.rar.001")
        assert cf.stem == "my release-grp"
        assert cf.qualifier == "sample"
        assert cf.volume == ".part1"
        assert cf.extension == ".rar"
        assert cf.split == ".001"


# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------

class TestGrouping:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_single_rar_release_one_container(self):
        paths = self._paths([
            "Cool.Release-GRP.rar",
            "Cool.Release-GRP.r00",
            "Cool.Release-GRP.r01",
            "Cool.Release-GRP.nfo",
            "Cool.Release-GRP.par2",
            "Cool.Release-GRP.vol0+1.par2",
            "front.jpg",
            "back.jpg",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1
        assert len(containers[0].files) == 8

    def test_two_distinct_releases(self):
        paths = self._paths([
            "Release.A-GRP.rar",
            "Release.A-GRP.r00",
            "Release.A-GRP.nfo",
            "Release.B-OTHERGRP.rar",
            "Release.B-OTHERGRP.r00",
            "Release.B-OTHERGRP.nfo",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 2

    def test_single_video(self):
        paths = self._paths([
            "Great.Movie.2024.720p-GRP.mkv",
            "Great.Movie.2024.720p-GRP.nfo",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1
        assert len(containers[0].playable) == 1

    def test_video_with_sample(self):
        paths = self._paths([
            "Great.Movie.2024.720p-GRP.mkv",
            "Great.Movie.2024.720p-GRP-sample.mkv",
            "Great.Movie.2024.720p-GRP.nfo",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1
        assert len(containers[0].playable) == 1
        assert len(containers[0].sample) == 1

    def test_image_set(self):
        paths = self._paths([
            "flowers_001.jpg",
            "flowers_002.jpg",
            "flowers_003.jpg",
            "front.jpg",
            "index.jpg",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1

    def test_empty_input(self):
        containers = MediaContainer.from_paths([])
        assert containers == []

    def test_single_file_valid_type(self):
        containers = MediaContainer.from_paths([Path("movie.mkv")])
        assert len(containers) == 1
        assert len(containers[0].playable) == 1

    def test_accessory_images_attach_to_dominant(self):
        paths = self._paths([
            "release.rar",
            "release.r00",
            "front.jpg",
            "back.jpg",
            "screen.jpg",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1
        assert len(containers[0].artwork) == 3

    def test_unaffiliated_catch_all(self):
        paths = self._paths([
            "randomfile.xyz",
            "anotherfile.abc",
            "something.dat",
        ])
        containers = MediaContainer.from_paths(paths)
        # Should have one unaffiliated container
        unaffiliated = [c for c in containers if c.unaffiliated]
        assert len(unaffiliated) == 1
        assert len(unaffiliated[0].files) == 3


# ---------------------------------------------------------------------------
# List assignment
# ---------------------------------------------------------------------------

class TestListAssignment:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_archives_in_archive_list(self):
        paths = self._paths([
            "release.rar", "release.r00", "release.r01",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers[0].archives) == 3

    def test_par_files_in_par_list(self):
        paths = self._paths([
            "release.rar",
            "release.par2",
            "release.vol0+1.par2",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers[0].par_files) == 2

    def test_text_files_in_text_list(self):
        paths = self._paths([
            "release.rar",
            "release.nfo",
            "readme.txt",
        ])
        containers = MediaContainer.from_paths(paths)
        # nfo and txt both in text_files (only those with matching stem)
        assert any(f.extension == ".nfo" for f in containers[0].text_files)

    def test_nzb_in_nzb_list(self):
        paths = self._paths([
            "release.rar",
            "release.nzb",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers[0].nzb) == 1

    def test_split_media_in_split_list(self):
        paths = self._paths([
            "big.movie.avi.001",
            "big.movie.avi.002",
            "big.movie.avi.003",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers[0].split_media) == 3

    def test_artwork_from_accessory_names(self):
        paths = self._paths([
            "release.rar",
            "front.jpg",
            "back.jpg",
            "cover.png",
            "screen.jpg",
            "index.jpg",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers[0].artwork) == 5


# ---------------------------------------------------------------------------
# Primary archive selection
# ---------------------------------------------------------------------------

class TestPrimaryArchive:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_rar_is_primary(self):
        paths = self._paths([
            "release.rar", "release.r00", "release.r01",
        ])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].primary_archive.path.name == "release.rar"

    def test_part1_is_primary(self):
        paths = self._paths([
            "release.part1.rar", "release.part2.rar", "release.part3.rar",
        ])
        containers = MediaContainer.from_paths(paths)
        assert "part1" in containers[0].primary_archive.path.name

    def test_001_is_primary_for_split(self):
        paths = self._paths([
            "release.rar.001", "release.rar.002", "release.rar.003",
        ])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].primary_archive.path.name == "release.rar.001"

    def test_single_zip_is_primary(self):
        paths = self._paths(["photos.zip"])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].primary_archive.path.name == "photos.zip"

    def test_missing_primary_flags_incomplete(self):
        """Only .r00+ volumes with no .rar → incomplete."""
        paths = self._paths([
            "release.r00", "release.r01", "release.r02",
        ])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].incomplete


# ---------------------------------------------------------------------------
# Extraction tool
# ---------------------------------------------------------------------------

class TestExtractionTool:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_rar_uses_unrar(self):
        paths = self._paths(["release.rar", "release.r00"])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].extraction_tool == "unrar"

    def test_zip_uses_unzip(self):
        paths = self._paths(["archive.zip"])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].extraction_tool in ("unzip", "7z")

    def test_7z_uses_7z(self):
        paths = self._paths(["archive.7z"])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].extraction_tool == "7z"

    def test_no_archives_no_tool(self):
        paths = self._paths(["movie.mkv"])
        containers = MediaContainer.from_paths(paths)
        assert containers[0].extraction_tool is None


# ---------------------------------------------------------------------------
# Scrambled filenames
# ---------------------------------------------------------------------------

class TestScrambledFilenames:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_hex_hash_rnn_detected_as_scrambled(self):
        paths = self._paths([
            "bc3eed3e69df8bcf3bb90d30ddeeebf451271b8c204f12a35beba0dd5e6328e1.rar",
            "bd827022004a1b3a57fa6152385f5cd70dabe29516c2aa522ad500928839baa6.r00",
            "be6d91234e57db7ec21dd0f06d1b96455e92ce9a05d22c85bb5478c07d6a61e8.r01",
            "c01ae13de93e84eba0f5893bb1a27ff07cfad0c9c8c6cef47ef9b0d191aee291.r02",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1
        assert containers[0].scrambled

    def test_normal_names_not_scrambled(self):
        paths = self._paths([
            "Cool.Release-GRP.rar",
            "Cool.Release-GRP.r00",
        ])
        containers = MediaContainer.from_paths(paths)
        assert not containers[0].scrambled


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------

class TestOrdering:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_archives_ordered_by_volume(self):
        paths = self._paths([
            "release.r02", "release.rar", "release.r00", "release.r01",
        ])
        containers = MediaContainer.from_paths(paths)
        names = [f.path.name for f in containers[0].archives]
        assert names == ["release.rar", "release.r00", "release.r01", "release.r02"]

    def test_playable_ordered_by_name(self):
        paths = self._paths([
            "movie.cd2.mkv", "movie.cd1.mkv",
        ])
        containers = MediaContainer.from_paths(paths)
        names = [f.path.name for f in containers[0].playable]
        assert names == ["movie.cd1.mkv", "movie.cd2.mkv"]

    def test_split_media_ordered_by_split_number(self):
        paths = self._paths([
            "movie.avi.003", "movie.avi.001", "movie.avi.002",
        ])
        containers = MediaContainer.from_paths(paths)
        names = [f.path.name for f in containers[0].split_media]
        assert names == ["movie.avi.001", "movie.avi.002", "movie.avi.003"]


# ---------------------------------------------------------------------------
# Mixed content
# ---------------------------------------------------------------------------

class TestMixedContent:

    @staticmethod
    def _paths(filenames: list[str]) -> list[Path]:
        return [Path(f) for f in filenames]

    def test_video_and_archive_same_container(self):
        paths = self._paths([
            "My.Movie-GRP.mkv",
            "My.Movie-GRP.rar",
            "My.Movie-GRP.r00",
            "My.Movie-GRP.nfo",
            "front.jpg",
        ])
        containers = MediaContainer.from_paths(paths)
        assert len(containers) == 1
        assert len(containers[0].playable) == 1
        assert len(containers[0].archives) == 2
        assert len(containers[0].artwork) == 1
        assert len(containers[0].text_files) == 1
