"""
# MediaContainer — Library for identifying and grouping media files.

## Calling API
- `MediaContainer.from_paths(paths: list[Path]) -> list[MediaContainer]`:
  Primary entry point to classify and group a list of files.
- `ClassifiedFile`: Represents a single file with its classification metadata.
- `FileType`: Enum of all recognized file types.

## Algorithmic Methodology
- **Stem Extraction**: Iterative right-to-left peeling of recognized suffixes
  (split, volume, extension) and stripping of qualifiers.
- **Grouping**: longest common prefix clustering on normalized stems.
- **Scrambled Detection**: Identifies obfuscated filenames by extension patterns.
- **List Assignment**: Distributes files into content-specific lists (playable,
  archives, artwork, etc.) based on classification and naming.

## Program Flow
1. Receive a list of `Path` objects.
2. For each path, create a `ClassifiedFile` (peel suffixes, strip qualifiers).
3. Group the `ClassifiedFile` objects by their normalized stems using a longest
   common prefix algorithm.
4. For each group, create a `MediaContainer`.
5. Populate container content lists and detect primary archive/extraction tool.
6. Identify and group scrambled filenames if present.
7. Return the final list of `MediaContainer` instances.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class FileType(Enum):
    VIDEO = auto()
    IMAGE = auto()
    ARCHIVE = auto()
    MULTIPART_ARCHIVE = auto()
    SPLIT_FILE = auto()
    PAR = auto()
    PAR2 = auto()
    TEXT = auto()
    NZB = auto()
    OTHER = auto()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VIDEO_EXTS = {
    ".avi", ".mkv", ".mp4", ".m4v", ".wmv", ".flv", ".mov", ".mpg", ".mpeg",
    ".ts", ".vob", ".ogm", ".divx", ".webm"
}
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"
}
ARCHIVE_EXTS = {".rar", ".zip", ".7z"}
TEXT_EXTS = {".txt", ".nfo"}

# Suffix patterns for peeling
RE_SPLIT = re.compile(r"\.\d{3}$")
RE_RAR_VOL = re.compile(r"\.[rs]\d{2}$", re.IGNORECASE)
RE_PART_VOL = re.compile(r"\.part\d+$", re.IGNORECASE)
RE_PAR2_VOL = re.compile(r"\.vol\d+\+\d+$", re.IGNORECASE)

# Qualifiers to strip
QUALIFIERS = {"sample", "screenshot", "subs", "proof", "covers"}

# Generic accessory names
ACCESSORY_NAMES = {
    "front", "back", "cover", "screen", "screens", "screenshot", "folder",
    "poster", "thumb", "fanart", "banner", "disc", "disk", "index", "clean"
}


@dataclass(frozen=True)
class ClassifiedFile:
    path: Path
    file_type: FileType
    stem: str
    qualifier: str | None = None
    volume: str | None = None
    extension: str = ""
    split: str | None = None

    @classmethod
    def from_filename(cls, filename: str) -> ClassifiedFile:
        return cls.from_path(Path(filename))

    @classmethod
    def from_path(cls, path: Path) -> ClassifiedFile:
        filename = path.name
        lower_name = filename.lower()

        # Initial classification by extension
        file_type = FileType.OTHER
        ext = path.suffix.lower()

        # Handle compound extensions like .rar.001
        if (m := RE_SPLIT.search(lower_name)):
            m.group()
            file_type = FileType.SPLIT_FILE
            # If it's something.rar.001, we want the .rar too
            remaining = filename[:-4]
            ext = Path(remaining).suffix.lower()
        elif RE_RAR_VOL.search(lower_name) or RE_PART_VOL.search(lower_name):
            file_type = FileType.MULTIPART_ARCHIVE
        elif ext == ".par2" or RE_PAR2_VOL.search(lower_name):
            file_type = FileType.PAR2
        elif ext in VIDEO_EXTS:
            file_type = FileType.VIDEO
        elif ext in IMAGE_EXTS:
            file_type = FileType.IMAGE
        elif ext in ARCHIVE_EXTS:
            file_type = FileType.ARCHIVE
        elif ext == ".par":
            file_type = FileType.PAR
        elif ext in TEXT_EXTS:
            file_type = FileType.TEXT
        elif ext == ".nzb":
            file_type = FileType.NZB

        # Peeling logic
        peeled_name = filename
        found_split = None
        found_volume = None
        found_ext = ""

        # Loop-based peeling
        while True:
            changed = False
            # Split
            if not found_split and (m := RE_SPLIT.search(peeled_name)):
                found_split = m.group()
                peeled_name = peeled_name[:-len(found_split)]
                changed = True
                continue
            
            # Volume (check this before extension for .part1.rar)
            m = RE_RAR_VOL.search(peeled_name) or RE_PART_VOL.search(peeled_name) or RE_PAR2_VOL.search(peeled_name)
            if m:
                if not found_volume:
                    found_volume = m.group()
                peeled_name = peeled_name[:-len(m.group())]
                changed = True
                continue

            # Extension
            temp_path = Path(peeled_name)
            temp_ext = temp_path.suffix.lower()
            if temp_ext in (VIDEO_EXTS | IMAGE_EXTS | ARCHIVE_EXTS | TEXT_EXTS | {".par", ".par2", ".nzb"}):
                if not found_ext:
                    found_ext = temp_ext
                peeled_name = peeled_name[:-len(temp_ext)]
                changed = True
                continue
            
            if not changed:
                break

        # Strip Qualifier
        stem = Path(peeled_name).name
        found_qualifier = None
        for q in QUALIFIERS:
            # Match -sample or _sample
            pattern = rf"[-_]{q}$"
            if re.search(pattern, stem, re.IGNORECASE):
                found_qualifier = q
                stem = re.sub(pattern, "", stem, flags=re.IGNORECASE)
                break

        # Normalize Stem
        normalized_stem = stem.lower()
        normalized_stem = re.sub(r"[._]", " ", normalized_stem).strip()

        # Re-check file type if it was just SPLIT_FILE
        if file_type == FileType.SPLIT_FILE and found_ext in ARCHIVE_EXTS:
            # We keep it as SPLIT_FILE for now as per tests
            pass
        
        # If it matches a multipart pattern but was identified as something else
        if found_volume and file_type not in (FileType.MULTIPART_ARCHIVE, FileType.PAR2):
             if found_ext == ".rar" or RE_RAR_VOL.match(found_volume):
                 file_type = FileType.MULTIPART_ARCHIVE

        return cls(
            path=path,
            file_type=file_type,
            stem=normalized_stem,
            qualifier=found_qualifier,
            volume=found_volume,
            extension=found_ext,
            split=found_split
        )


@dataclass
class MediaContainer:
    name: str
    files: list[ClassifiedFile] = field(default_factory=list)
    scrambled: bool = False
    unaffiliated: bool = False

    # Content lists
    playable: list[ClassifiedFile] = field(default_factory=list)
    sample: list[ClassifiedFile] = field(default_factory=list)
    artwork: list[ClassifiedFile] = field(default_factory=list)
    archives: list[ClassifiedFile] = field(default_factory=list)
    par_files: list[ClassifiedFile] = field(default_factory=list)
    split_media: list[ClassifiedFile] = field(default_factory=list)
    text_files: list[ClassifiedFile] = field(default_factory=list)
    nzb: list[ClassifiedFile] = field(default_factory=list)
    misc: list[ClassifiedFile] = field(default_factory=list)

    @classmethod
    def from_paths(cls, paths: list[Path]) -> list[MediaContainer]:
        if not paths:
            return []

        classified = [ClassifiedFile.from_path(p) for p in paths]

        # 1. Separate files into categories
        # Scrambled clusters
        scrambled_groups = cls._find_scrambled_groups(classified)
        scrambled_files = {f for group in scrambled_groups for f in group}
        
        remaining = [f for f in classified if f not in scrambled_files]
        
        # Accessories
        accessory_files = [
            f for f in remaining 
            if f.stem in ACCESSORY_NAMES and f.file_type in (FileType.IMAGE, FileType.TEXT)
        ]
        remaining = [f for f in remaining if f not in accessory_files]
        
        # Proper files (must have a recognized type or be grouped)
        proper_files = [f for f in remaining if f.file_type != FileType.OTHER]
        others = [f for f in remaining if f.file_type == FileType.OTHER]
        
        # 2. Group proper files by longest common prefix
        prefix_groups = cls._get_longest_common_prefix_groups(proper_files)
        
        # 3. Create containers
        containers: list[MediaContainer] = []
        
        # Scrambled containers
        for group in scrambled_groups:
            mc = cls(name=group[0].stem, files=group, scrambled=True)
            containers.append(mc)
            
        # longest common prefix containers
        for group_name, group in prefix_groups.items():
            mc = cls(name=group_name, files=group)
            containers.append(mc)

        # 4. Attach Accessories & Others
        # If we have containers, try to attach accessories and others to them
        if containers:
            # Sort containers by importance for attachment
            # Playable/Archives > others
            containers.sort(key=lambda c: (
                any(f.file_type == FileType.VIDEO for f in c.files),
                any(f.file_type in (FileType.ARCHIVE, FileType.MULTIPART_ARCHIVE) for f in c.files),
                len(c.files)
            ), reverse=True)
            
            dominant = containers[0]
            
            # Attach accessories to dominant
            dominant.files.extend(accessory_files)
            
            # For others, try to match by stem prefix, else attach to dominant if no peers
            for f in others:
                found = False
                for mc in containers:
                    if f.stem.startswith(mc.name) or mc.name.startswith(f.stem):
                        mc.files.append(f)
                        found = True
                        break
                if not found:
                    # If it's the only container, attach it
                    if len(containers) == 1:
                        dominant.files.append(f)
                    else:
                        # Will go to unaffiliated
                        pass
        elif accessory_files or others:
            # If no proper containers, but we have accessories/others
            if accessory_files:
                mc = cls(name="accessories", files=accessory_files)
                containers.append(mc)
                # Attach others to it
                mc.files.extend([f for f in others])
            else:
                # Only others
                pass

        # 5. Handle remaining unaffiliated
        all_assigned = {f for mc in containers for f in mc.files}
        still_unaffiliated = [f for f in others if f not in all_assigned]
        
        if still_unaffiliated:
            mc = cls(name="unaffiliated", files=still_unaffiliated, unaffiliated=True)
            containers.append(mc)

        # 6. Finalize containers
        for mc in containers:
            mc._assign_lists()
            mc._sort_lists()
            
        return containers

    @classmethod
    def _find_scrambled_groups(cls, files: list[ClassifiedFile]) -> list[list[ClassifiedFile]]:
        scrambled_candidates = [f for f in files if cls._is_scrambled_stem(f.stem)]
        if not scrambled_candidates:
            return []
            
        groups = defaultdict(list)
        for f in scrambled_candidates:
            # Group by stem length
            groups[len(f.stem)].append(f)
            
        result = []
        for length, group in groups.items():
            if len(group) >= 2:
                result.append(group)
        return result

    @staticmethod
    def _is_scrambled_stem(stem: str) -> bool:
        if not stem:
            return False
        if any(c in " _-" for c in stem):
            return False
        if not stem.isalnum():
            return False
        # Heuristic: long hash-like strings
        return len(stem) >= 20

    @staticmethod
    def _get_longest_common_prefix_groups(files: list[ClassifiedFile]) -> dict[str, list[ClassifiedFile]]:
        if not files:
            return {}
            
        sorted_files = sorted(files, key=lambda f: f.stem)
        
        groups: list[list[ClassifiedFile]] = []
        if sorted_files:
            current_group = [sorted_files[0]]
            for f in sorted_files[1:]:
                prev_f = current_group[-1]
                prefix = MediaContainer._calculate_longest_common_prefix(prev_f.stem, f.stem)
                
                significant = False
                prefix_len = len(prefix)
                max_len = max(len(prev_f.stem), len(f.stem))
                
                # Significance: shared prefix must be at least 70% of the stems
                # OR be a full stem (prefix matching)
                if prefix_len >= 0.7 * max_len:
                    significant = True
                elif prefix == prev_f.stem or prefix == f.stem:
                    significant = True
                
                if significant:
                    current_group.append(f)
                else:
                    groups.append(current_group)
                    current_group = [f]
            groups.append(current_group)
            
        result = {}
        for group in groups:
            stems = [f.stem for f in group]
            prefix = stems[0]
            for s in stems[1:]:
                prefix = MediaContainer._calculate_longest_common_prefix(prefix, s)
            
            group_name = re.sub(r"[\s\d\-_.]+$", "", prefix).strip()
            if not group_name:
                group_name = stems[0]
            
            result[group_name] = group
            
        return result

    @staticmethod
    def _calculate_longest_common_prefix(s1: str, s2: str) -> str:
        prefix = ""
        for c1, c2 in zip(s1, s2):
            if c1 == c2:
                prefix += c1
            else:
                break
        return prefix

    def _assign_lists(self):
        for f in self.files:
            if f.qualifier == "sample":
                self.sample.append(f)
            elif f.file_type == FileType.IMAGE:
                self.artwork.append(f)
            elif f.file_type == FileType.VIDEO:
                self.playable.append(f)
            elif f.file_type in (FileType.ARCHIVE, FileType.MULTIPART_ARCHIVE):
                self.archives.append(f)
            elif f.file_type == FileType.SPLIT_FILE:
                if f.extension in ARCHIVE_EXTS:
                    self.archives.append(f)
                elif f.extension in VIDEO_EXTS:
                    self.split_media.append(f)
                else:
                    self.archives.append(f) # Default to archive for split
            elif f.file_type in (FileType.PAR, FileType.PAR2):
                self.par_files.append(f)
            elif f.file_type == FileType.TEXT:
                self.text_files.append(f)
            elif f.file_type == FileType.NZB:
                self.nzb.append(f)
            else:
                self.misc.append(f)

    def _sort_lists(self):
        # Archives ordered by volume/split
        self.archives.sort(key=lambda f: (f.volume or "", f.split or ""))
        # Playable ordered by name
        self.playable.sort(key=lambda f: f.path.name.lower())
        # Split media ordered by split
        self.split_media.sort(key=lambda f: f.split or "")

    @property
    def primary_archive(self) -> ClassifiedFile | None:
        if not self.archives:
            return None
        # the .rar file
        for f in self.archives:
            if f.extension == ".rar" and not f.volume and not f.split:
                return f
        # part1.rar
        for f in self.archives:
            if f.volume and (".part1" in f.volume.lower() or ".part01" in f.volume.lower()):
                return f
        # .001
        for f in self.archives:
            if f.split == ".001":
                return f
        # Single zip/7z
        for f in self.archives:
            if f.extension in (".zip", ".7z") and not f.volume and not f.split:
                return f
        return None

    @property
    def extraction_tool(self) -> str | None:
        pa = self.primary_archive
        if not pa:
            # Heuristic if primary missing but archives exist
            if any(f.extension == ".rar" or (f.volume and ".r" in f.volume.lower()) for f in self.archives):
                return "unrar"
            return None
        ext = pa.extension.lower()
        if ext == ".rar":
            return "unrar"
        if ext == ".zip":
            return "unzip"
        if ext == ".7z":
            return "7z"
        if pa.split == ".001":
            # Check what's before .001
            if ".rar" in pa.path.name.lower():
                return "unrar"
        return None

    @property
    def incomplete(self) -> bool:
        if self.archives and not self.primary_archive:
            return True
        return False

    @property
    def needs_extraction(self) -> bool:
        return bool(self.archives)
