"""
# MediaContainer — Library for identifying and grouping media files.

## Calling API
- `MediaContainer.from_paths(paths: list[Path], settings: SettingsProtocol | None = None, logger: LoggingProtocol | None = None) -> list[MediaContainer]`:
  Primary entry point to classify and group a list of files.
- `ClassifiedFile`: Represents a single file with its classification metadata.
- `FileType`: Enum of all recognized file types.

## Algorithmic Methodology
- **Rule-based Parser (DSL)**: Declarative rules for suffix peeling, sequence extraction, and qualifier stripping.
- **Grouping**: Longest common prefix clustering on normalized stems.
- **Visual Analysis**: Uses macOS `sips` to fingerprint images with weak stems (e.g. 1.jpg, 2.jpg) 
  to group them into logical galleries. Uses structural hashing (aHash) and color histograms.
- **Scrambled Detection**: Identifies obfuscated filenames by extension patterns.
- **List Assignment**: Distributes files into content-specific lists (video,
  archives, artwork, etc.) based on classification and naming.

## Program Flow
1. Receive a list of `Path` objects.
2. For each path, create a `ClassifiedFile` using the `Parser` (rules-based).
3. Group the `ClassifiedFile` objects by their normalized stems using a longest
   common prefix algorithm.
4. Perform visual analysis on images with "weak" stems to split or group them.
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
from typing import Any, Protocol, runtime_checkable

from .parser import Parser, ParseResult, SettingsProtocol
from .visual import VisualFingerprint


@runtime_checkable
class LoggingProtocol(Protocol):
    """Protocol defining the expected interface for system logging."""
    def log_error(self, ident: str, message: str) -> None: ...
    def log_warning(self, ident: str, message: str) -> None: ...
    def log_info(self, ident: str, message: str) -> None: ...


class DefaultLogger:
    """Minimal dummy implementation of the logging protocol."""
    def log_error(self, ident: str, message: str) -> None: pass
    def log_warning(self, ident: str, message: str) -> None: pass
    def log_info(self, ident: str, message: str) -> None: pass


class DefaultSettings:
    """Minimal dummy implementation of the settings protocol."""
    path: Path | None = None
    def get(self, key: str, default: Any = None) -> Any: return default
    def set(self, key: str, value: Any, save: bool = False) -> None: pass


class FileType(Enum):
    VIDEO = auto()
    IMAGE = auto()
    GALLERY = auto()
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

# Generic accessory names
ACCESSORY_NAMES = {
    "front", "back", "cover", "screen", "screens", "screenshot", "folder",
    "poster", "thumb", "fanart", "banner", "disc", "disk", "index", "clean",
    "cd", "dvd"
}


@dataclass(frozen=True)
class ClassifiedFile:
    path: Path
    file_type: FileType
    stem: str
    raw_stem: str
    qualifier: str | None = None
    volume: str | None = None
    extension: str = ""
    split: str | None = None
    sequence: str | None = None

    @classmethod
    def from_filename(cls, filename: str, settings: SettingsProtocol | None = None) -> ClassifiedFile:
        return cls.from_path(Path(filename), settings)

    @classmethod
    def from_path(cls, path: Path, settings: SettingsProtocol | None = None) -> ClassifiedFile:
        parser = Parser(settings)
        res = parser.parse(path)

        ext = res.extension.lower()
        split = res.split
        volume = res.volume
        sequence = res.sequence
        
        if not sequence and split and (ext in IMAGE_EXTS or ext == ""):
            sequence = split.lstrip(".")

        file_type = FileType.OTHER
        
        if volume:
            if volume.startswith(".vol") and (".par2" in path.name.lower() or ext == ".par2"):
                file_type = FileType.PAR2
            else:
                file_type = FileType.MULTIPART_ARCHIVE
        elif split:
            if ext in VIDEO_EXTS:
                file_type = FileType.VIDEO
            elif ext in IMAGE_EXTS:
                file_type = FileType.GALLERY
            else:
                file_type = FileType.SPLIT_FILE
        elif ext:
            if ext in VIDEO_EXTS:
                file_type = FileType.VIDEO
            elif ext in IMAGE_EXTS:
                if res.is_gallery_seq or (split and ext in IMAGE_EXTS):
                    file_type = FileType.GALLERY
                else:
                    file_type = FileType.IMAGE
            elif ext in ARCHIVE_EXTS:
                file_type = FileType.ARCHIVE
            elif ext == ".par2":
                file_type = FileType.PAR2
            elif ext == ".par":
                file_type = FileType.PAR
            elif ext in TEXT_EXTS:
                file_type = FileType.TEXT
            elif ext == ".nzb":
                file_type = FileType.NZB

        return cls(
            path=path,
            file_type=file_type,
            stem=res.stem,
            raw_stem=res.raw_stem,
            qualifier=res.qualifier,
            volume=volume,
            extension=ext,
            split=split,
            sequence=sequence
        )


@dataclass
class MediaContainer:
    name: str
    lcp: str = ""
    files: list[ClassifiedFile] = field(default_factory=list)
    settings: SettingsProtocol = field(default_factory=DefaultSettings)
    logger: LoggingProtocol = field(default_factory=DefaultLogger)
    scrambled: bool = False
    unaffiliated: bool = False
    _group_prefix: str = "" # Internal normalized prefix used for attachment

    # Content lists
    video: list[ClassifiedFile] = field(default_factory=list)
    sample: list[ClassifiedFile] = field(default_factory=list)
    gallery: list[ClassifiedFile] = field(default_factory=list)
    artwork: list[ClassifiedFile] = field(default_factory=list)
    archives: list[ClassifiedFile] = field(default_factory=list)
    par_files: list[ClassifiedFile] = field(default_factory=list)
    split_media: list[ClassifiedFile] = field(default_factory=list)
    text_files: list[ClassifiedFile] = field(default_factory=list)
    nzb: list[ClassifiedFile] = field(default_factory=list)
    misc: list[ClassifiedFile] = field(default_factory=list)

    @property
    def stem(self) -> str:
        """Alias for lcp (unmodified prefix)."""
        return self.lcp

    @classmethod
    def from_paths(
        cls,
        paths: list[Path],
        settings: SettingsProtocol | None = None,
        logger: LoggingProtocol | None = None
    ) -> list[MediaContainer]:
        if not paths:
            if logger:
                logger.log_warning("mediacontainer", "from_paths called with empty path list.")
            return []

        if settings is None:
            settings = DefaultSettings()
        if logger is None:
            logger = DefaultLogger()

        classified = [ClassifiedFile.from_path(p, settings) for p in paths]

        # 1. Scrambled Detection
        scrambled_groups = cls._find_scrambled_groups(classified)
        scrambled_files = {f for group in scrambled_groups for f in group}
        remaining = [f for f in classified if f not in scrambled_files]

        # 2. Accessory and Proper Identification
        accessory_files = [
            f for f in remaining 
            if f.stem in ACCESSORY_NAMES and f.file_type in (FileType.IMAGE, FileType.TEXT, FileType.GALLERY)
        ]
        remaining = [f for f in remaining if f not in accessory_files]

        proper_files = [f for f in remaining if f.file_type != FileType.OTHER]
        others = [f for f in remaining if f.file_type == FileType.OTHER]

        # 3. LCP Prefix Grouping
        prefix_groups = cls._get_longest_common_prefix_groups(proper_files)

        # 4. Container Creation
        containers: list[MediaContainer] = []

        for group in scrambled_groups:
            lcp = group[0].raw_stem
            mc = cls(name=cls._make_readable(lcp), lcp=lcp, files=group, settings=settings, logger=logger, scrambled=True, _group_prefix=group[0].stem)
            containers.append(mc)

        for group_prefix, group in prefix_groups.items():
            raw_stems = [f.raw_stem for f in group]
            lcp = raw_stems[0]
            for s in raw_stems[1:]:
                lcp = cls._calculate_longest_common_prefix(lcp, s)
            
            primary_files = [f for f in group if f.file_type in (FileType.VIDEO, FileType.GALLERY, FileType.ARCHIVE, FileType.MULTIPART_ARCHIVE)]
            if primary_files:
                primary_raw_stems = [f.raw_stem for f in primary_files]
                naming_lcp = primary_raw_stems[0]
                for s in primary_raw_stems[1:]:
                    naming_lcp = cls._calculate_longest_common_prefix(naming_lcp, s)
            else:
                naming_lcp = lcp

            mc = cls(name=cls._make_readable(naming_lcp), lcp=lcp, files=group, settings=settings, logger=logger, _group_prefix=group_prefix)
            containers.append(mc)

        # 5. Visual Analysis (Split/Merge weak containers)
        containers = cls._perform_visual_analysis(containers, settings, logger)

        # 6. Accessory and Other Attachment
        if containers:
            containers.sort(key=lambda c: (
                any(f.file_type == FileType.VIDEO for f in c.files),
                any(f.file_type in (FileType.ARCHIVE, FileType.MULTIPART_ARCHIVE) for f in c.files),
                len(c.files)
            ), reverse=True)

            dominant = containers[0]
            dominant.files.extend(accessory_files)

            for f in others:
                found = False
                for mc in containers:
                    if mc._group_prefix and (f.stem.startswith(mc._group_prefix) or mc._group_prefix.startswith(f.stem)):
                        mc.files.append(f)
                        found = True
                        break
                if not found:
                    if len(containers) == 1:
                        dominant.files.append(f)

        # 7. Unaffiliated catch-all
        all_assigned = {f for mc in containers for f in mc.files}
        still_unaffiliated = [f for f in others if f not in all_assigned]

        if still_unaffiliated:
            mc = cls(name="unaffiliated", lcp="unaffiliated", files=still_unaffiliated, settings=settings, logger=logger, unaffiliated=True)
            containers.append(mc)

        # 8. Finalize lists
        for mc in containers:
            mc._assign_lists()
            mc._sort_lists()

        return containers

    @classmethod
    def _perform_visual_analysis(cls, containers: list[MediaContainer], settings: SettingsProtocol, logger: LoggingProtocol) -> list[MediaContainer]:
        """Perform visual analysis on images in 'weak' containers to regroup them."""
        def is_weak(c: MediaContainer) -> bool:
            return not c.name or (len(c.name) <= 2 and c.name.isdigit())

        # 1. Identify weak containers and extract all images
        weak_containers = [c for c in containers if is_weak(c)]
        if not weak_containers:
            return containers

        remaining_containers = [c for c in containers if c not in weak_containers]
        
        all_weak_files: list[ClassifiedFile] = []
        for c in weak_containers:
            all_weak_files.extend(c.files)

        image_files = [f for f in all_weak_files if f.file_type in (FileType.IMAGE, FileType.GALLERY) and f.path.exists()]
        non_image_files = [f for f in all_weak_files if f not in image_files]

        if not image_files:
            return containers

        # 2. Compute fingerprints and histograms
        fingerprints: dict[Path, str] = {}
        histograms: dict[Path, list[int]] = {}
        for f in image_files:
            fp = VisualFingerprint.get_fingerprint(f.path)
            if fp: fingerprints[f.path] = fp
            
            hist = VisualFingerprint.get_histogram(f.path)
            if hist: histograms[f.path] = hist

        # 3. Cluster images by visual similarity
        clusters: list[list[ClassifiedFile]] = []
        visited_paths = set()

        for i, f1 in enumerate(image_files):
            if f1.path in visited_paths: continue
            
            fp1 = fingerprints.get(f1.path)
            hist1 = histograms.get(f1.path)
            if not fp1 and not hist1: continue

            current_cluster = [f1]
            visited_paths.add(f1.path)
            
            for f2 in image_files[i+1:]:
                if f2.path in visited_paths: continue
                fp2 = fingerprints.get(f2.path)
                hist2 = histograms.get(f2.path)
                
                match = False
                # Strategy 1: Structural Match (aHash Hamming distance <= 10)
                if fp1 and fp2 and VisualFingerprint.calculate_distance(fp1, fp2) <= 10:
                    match = True
                
                # Strategy 2: Pictorial/Color Match (Histogram Correlation >= 0.95)
                # This helps with crops/related images from same set
                if not match and hist1 and hist2:
                    corr = VisualFingerprint.calculate_histogram_correlation(hist1, hist2)
                    if corr >= 0.95:
                        match = True
                
                if match:
                    current_cluster.append(f2)
                    visited_paths.add(f2.path)
            
            clusters.append(current_cluster)

        # 4. Create new containers from clusters
        new_containers = remaining_containers
        
        for cluster in clusters:
            # Generate a stable name
            first_img_path = cluster[0].path
            fp = fingerprints.get(first_img_path)
            if fp:
                hash_suffix = format(int(fp, 2), 'x')[:8]
            else:
                hash_suffix = "unknown"
            
            mc = cls(
                name=f"[Gallery-{hash_suffix}]",
                lcp=f"visual-group-{hash_suffix}",
                files=cluster,
                settings=settings,
                logger=logger
            )
            new_containers.append(mc)

        # 5. Handle orphans
        orphans = [f for f in image_files if f.path not in visited_paths] + non_image_files
        for f in orphans:
            mc = cls(name=cls._make_readable(f.raw_stem), lcp=f.raw_stem, files=[f], settings=settings, logger=logger)
            new_containers.append(mc)

        return new_containers

    @classmethod
    def _make_readable(cls, s: str) -> str:
        """Transform LCP into a clean, maximal readable name."""
        if not s: return ""
        counts = {".": s.count("."), "_": s.count("_"), "-": s.count("-")}
        best_sep = "."
        max_count = 0
        for sep in [".", "_", "-"]:
            if counts[sep] > max_count:
                max_count = counts[sep]
                best_sep = sep
        s = re.sub(r"[()\[\]]", "", s)
        s = re.sub(r"[._-]", " ", s)
        s = re.sub(r"[^\w]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        s = s.replace(" ", best_sep)
        if best_sep:
            pattern = re.escape(best_sep) + r"{2,}"
            s = re.sub(pattern, best_sep, s)
        return s.strip(best_sep + " ")

    @classmethod
    def _find_scrambled_groups(cls, files: list[ClassifiedFile]) -> list[list[ClassifiedFile]]:
        scrambled_candidates = [f for f in files if cls._is_scrambled_stem(f.stem)]
        if not scrambled_candidates:
            return []
        groups = defaultdict(list)
        for f in scrambled_candidates:
            groups[len(f.stem)].append(f)
        result = []
        for length, group in groups.items():
            if len(group) >= 2:
                result.append(group)
        return result

    @staticmethod
    def _is_scrambled_stem(stem: str) -> bool:
        if not stem or any(c in " _-" for c in stem) or not stem.isalnum():
            return False
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
                if prefix_len >= 0.7 * max_len or prefix == prev_f.stem or prefix == f.stem:
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

    def _assign_lists(self) -> None:
        for f in self.files:
            if f.qualifier == "sample":
                self.sample.append(f)
            elif f.file_type == FileType.GALLERY:
                self.gallery.append(f)
            elif f.file_type == FileType.IMAGE:
                self.artwork.append(f)
            elif f.file_type == FileType.VIDEO:
                self.video.append(f)
            elif f.file_type in (FileType.ARCHIVE, FileType.MULTIPART_ARCHIVE):
                self.archives.append(f)
            elif f.file_type == FileType.SPLIT_FILE:
                self.archives.append(f)
            elif f.file_type in (FileType.PAR, FileType.PAR2):
                self.par_files.append(f)
            elif f.file_type == FileType.TEXT:
                self.text_files.append(f)
            elif f.file_type == FileType.NZB:
                self.nzb.append(f)
            else:
                self.misc.append(f)

        for f in list(self.video):
            if f.split:
                self.video.remove(f)
                self.split_media.append(f)

    def _sort_lists(self) -> None:
        self.archives.sort(key=lambda f: (f.volume or "", f.split or ""))
        self.video.sort(key=lambda f: f.path.name.lower())
        self.gallery.sort(key=lambda f: f.path.name.lower())
        self.split_media.sort(key=lambda f: f.split or "")

    @property
    def primary_archive(self) -> ClassifiedFile | None:
        if not self.archives:
            return None
        for f in self.archives:
            if f.extension == ".rar" and not f.volume and not f.split:
                return f
        for f in self.archives:
            if f.volume and (".part1" in f.volume.lower() or ".part01" in f.volume.lower()):
                return f
        for f in self.archives:
            if f.split == ".001":
                return f
        for f in self.archives:
            if f.extension in (".zip", ".7z") and not f.volume and not f.split:
                return f
        return None

    @property
    def extraction_tool(self) -> str | None:
        pa = self.primary_archive
        if not pa:
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
            if ".rar" in pa.path.name.lower():
                return "unrar"
            elif ".7z" in pa.path.name.lower():
                return "7z"
            elif ".zip" in pa.path.name.lower():
                return "unzip"
            if ".rar" in pa.path.name.lower():
                return "unrar"
            if ".7z" in pa.path.name.lower():
                return "7z"
        return None

    @property
    def incomplete(self) -> bool:
        if self.archives and not self.primary_archive:
            return True
        return False

    @property
    def needs_extraction(self) -> bool:
        return bool(self.archives)
