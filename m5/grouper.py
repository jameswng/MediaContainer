"""Group classified files into MediaObjects."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from .classify import (
    ACCESSORY_IMAGE_NAMES,
    ClassifiedFile,
    FileType,
    classify_directory,
)


@dataclass
class MediaObject:
    """A logical media object composed of related files."""
    name: str
    files: list[ClassifiedFile] = field(default_factory=list)

    @property
    def has_archives(self) -> bool:
        return any(
            f.file_type in (FileType.ARCHIVE, FileType.SPLIT_ARCHIVE)
            for f in self.files
        )

    @property
    def videos(self) -> list[ClassifiedFile]:
        return [f for f in self.files if f.file_type == FileType.VIDEO]

    @property
    def images(self) -> list[ClassifiedFile]:
        return [f for f in self.files if f.file_type == FileType.IMAGE]

    @property
    def archives(self) -> list[ClassifiedFile]:
        return [
            f for f in self.files
            if f.file_type in (FileType.ARCHIVE, FileType.SPLIT_ARCHIVE)
        ]

    @property
    def par_files(self) -> list[ClassifiedFile]:
        return [
            f for f in self.files
            if f.file_type in (FileType.PAR, FileType.PAR2)
        ]

    @property
    def needs_extraction(self) -> bool:
        return self.has_archives

    def add(self, cf: ClassifiedFile) -> None:
        self.files.append(cf)

    def __repr__(self) -> str:
        types = defaultdict(int)
        for f in self.files:
            types[f.file_type.name] += 1
        summary = ", ".join(f"{v} {k.lower()}" for k, v in sorted(types.items()))
        return f"MediaObject({self.name!r}, [{summary}])"


def group_files(directory: Path) -> list[MediaObject]:
    """Scan a directory and group files into MediaObjects.

    Strategy:
    1. Classify all files.
    2. Identify "anchor" files — archives and videos that define media objects.
    3. Build initial groups around anchors using base_name matching.
    4. Attach "accessory" files (images, nfo, subtitles, par) to the
       best-matching group.
    5. If no anchors exist, treat the whole directory as one media object.
    """
    classified = classify_directory(directory)
    if not classified:
        return []

    # Phase 1: Find anchor files (archives, videos — the core identity)
    anchors: list[ClassifiedFile] = []
    accessories: list[ClassifiedFile] = []

    for cf in classified:
        if cf.file_type in (
            FileType.ARCHIVE, FileType.SPLIT_ARCHIVE, FileType.VIDEO,
        ):
            anchors.append(cf)
        else:
            accessories.append(cf)

    # Phase 2: Cluster anchors by base_name
    groups: dict[str, MediaObject] = {}

    for anchor in anchors:
        matched_key = _find_matching_group(anchor.base_name, groups)
        if matched_key:
            groups[matched_key].add(anchor)
        else:
            # New group — use this anchor's base_name as the group key
            mo = MediaObject(name=anchor.base_name)
            mo.add(anchor)
            groups[anchor.base_name] = mo

    # Phase 3: If no anchors, everything is one media object
    if not groups:
        mo = MediaObject(name=directory.name)
        for cf in classified:
            mo.add(cf)
        return [mo]

    # Phase 4: Attach accessories to best-matching group
    for acc in accessories:
        # Check if this is a generic accessory image (front.jpg, etc.)
        stem_lower = acc.path.stem.lower()
        is_generic_accessory = (
            acc.file_type == FileType.IMAGE
            and stem_lower in ACCESSORY_IMAGE_NAMES
        )

        if is_generic_accessory and len(groups) == 1:
            # Only one group — attach directly
            next(iter(groups.values())).add(acc)
        elif is_generic_accessory and len(groups) > 1:
            # Multiple groups — attach to the first (dominant) one
            # TODO: smarter heuristic when there are subfolder clues
            next(iter(groups.values())).add(acc)
        else:
            # Try to match by base_name similarity
            best_key = _find_best_group(acc.base_name, groups)
            if best_key:
                groups[best_key].add(acc)
            else:
                # Attach to the first group as fallback
                next(iter(groups.values())).add(acc)

    return list(groups.values())


def _find_matching_group(
    base_name: str,
    groups: dict[str, MediaObject],
    threshold: float = 0.95,
) -> str | None:
    """Find an existing group whose key is similar enough to base_name."""
    if not groups:
        return None

    best_key = None
    best_score = 0.0

    for key in groups:
        # Exact match
        if base_name == key:
            return key

        score = SequenceMatcher(None, base_name, key).ratio()
        if score > best_score:
            best_score = score
            best_key = key

    if best_score >= threshold:
        return best_key
    return None


def _find_best_group(
    base_name: str,
    groups: dict[str, MediaObject],
    threshold: float = 0.4,
) -> str | None:
    """Find the best matching group for an accessory file.

    Uses a lower threshold than anchor matching since accessories
    may have looser naming (e.g., 'archive_screenshot' vs 'archive').
    """
    if not groups:
        return None

    best_key = None
    best_score = 0.0

    for key in groups:
        # Check substring containment
        if key in base_name or base_name in key:
            return key

        score = SequenceMatcher(None, base_name, key).ratio()
        if score > best_score:
            best_score = score
            best_key = key

    if best_score >= threshold:
        return best_key
    return None
