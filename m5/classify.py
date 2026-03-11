"""Classify files by type and extract normalized base names."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class FileType(Enum):
    VIDEO = auto()
    IMAGE = auto()
    ARCHIVE = auto()
    SPLIT_ARCHIVE = auto()  # .r00-.r99, .s00, .001-.999
    PAR = auto()
    PAR2 = auto()
    AUDIO = auto()
    SUBTITLE = auto()
    NFO = auto()
    OTHER = auto()


VIDEO_EXTS = frozenset({
    ".avi", ".mkv", ".mp4", ".m4v", ".wmv", ".flv", ".mov",
    ".mpg", ".mpeg", ".ts", ".vob", ".ogm", ".divx", ".webm",
})

IMAGE_EXTS = frozenset({
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp",
})

ARCHIVE_EXTS = frozenset({
    ".rar", ".zip", ".7z", ".tar", ".gz", ".bz2", ".xz",
    ".tar.gz", ".tar.bz2", ".tar.xz", ".tgz",
})

AUDIO_EXTS = frozenset({
    ".mp3", ".flac", ".ogg", ".wav", ".aac", ".wma", ".m4a",
})

SUBTITLE_EXTS = frozenset({
    ".srt", ".sub", ".idx", ".ass", ".ssa", ".vtt",
})

# Matches RAR split volumes: .r00-.r99, .s00-.s99
_RAR_SPLIT_RE = re.compile(r"\.[rs]\d{2}$", re.IGNORECASE)

# Matches numeric split files: .001, .002, etc.
_NUMERIC_SPLIT_RE = re.compile(r"\.\d{3}$")

# Matches par files: .par, .p01, .p02, etc.
_PAR_RE = re.compile(r"\.par$", re.IGNORECASE)

# Matches par2 files: .par2, .vol0+1.par2, etc.
_PAR2_RE = re.compile(r"\.vol\d+\+\d+\.par2$|\.par2$", re.IGNORECASE)

# Common "accessory" image names that likely belong to a media object
ACCESSORY_IMAGE_NAMES = frozenset({
    "front", "back", "cover", "screen", "screens", "screenshot",
    "folder", "poster", "thumb", "fanart", "banner", "disc", "disk",
})


@dataclass
class ClassifiedFile:
    """A file with its classified type and normalized base name."""
    path: Path
    file_type: FileType
    base_name: str  # normalized stem for grouping

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def suffix(self) -> str:
        return self.path.suffix.lower()


def classify(path: Path) -> ClassifiedFile:
    """Classify a single file and extract its normalized base name."""
    name = path.name
    lower = name.lower()
    suffix = path.suffix.lower()

    file_type = _detect_type(lower, suffix)
    base_name = _extract_base_name(path, file_type)

    return ClassifiedFile(path=path, file_type=file_type, base_name=base_name)


def _detect_type(lower_name: str, suffix: str) -> FileType:
    """Determine the FileType for a filename."""
    if _PAR2_RE.search(lower_name):
        return FileType.PAR2
    if _PAR_RE.search(lower_name):
        return FileType.PAR
    if _RAR_SPLIT_RE.search(lower_name):
        return FileType.SPLIT_ARCHIVE
    if _NUMERIC_SPLIT_RE.search(lower_name):
        return FileType.SPLIT_ARCHIVE
    if suffix in VIDEO_EXTS:
        return FileType.VIDEO
    if suffix in IMAGE_EXTS:
        return FileType.IMAGE
    if suffix in ARCHIVE_EXTS:
        return FileType.ARCHIVE
    if suffix in AUDIO_EXTS:
        return FileType.AUDIO
    if suffix in SUBTITLE_EXTS:
        return FileType.SUBTITLE
    if suffix == ".nfo":
        return FileType.NFO
    return FileType.OTHER


def _extract_base_name(path: Path, file_type: FileType) -> str:
    """Extract a normalized base name for grouping purposes.

    Strips split suffixes, volume indicators, and normalizes casing/separators
    so that related files cluster together.
    """
    stem = path.stem

    # For par2 files, strip .volN+N before .par2
    if file_type == FileType.PAR2:
        stem = re.sub(r"\.vol\d+\+\d+$", "", stem, flags=re.IGNORECASE)
        # Also strip the .par2 that might be left in compound extensions
        stem = re.sub(r"\.par2$", "", stem, flags=re.IGNORECASE)

    # For split archives, strip the split suffix to get the archive base
    if file_type == FileType.SPLIT_ARCHIVE:
        # The suffix (.r00, .001) is already stripped by .stem
        # but if there's a compound like foo.rar -> stem is already "foo"
        pass

    # For RAR archives, stem is already the base name (e.g., "foo" from "foo.rar")

    # Normalize: lowercase and collapse separators
    normalized = stem.lower()
    # Replace common separators with a single space for comparison
    normalized = re.sub(r"[\s._]+", " ", normalized).strip()

    return normalized


def classify_directory(directory: Path) -> list[ClassifiedFile]:
    """Classify all files in a directory (non-recursive)."""
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")

    return sorted(
        [classify(f) for f in directory.iterdir() if f.is_file()],
        key=lambda cf: cf.name.lower(),
    )
