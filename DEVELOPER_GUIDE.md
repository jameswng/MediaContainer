# MediaContainer — Developer's Guide

> Primary documentation for MediaContainer library consumers.

## Installation

```bash
git clone https://github.com/iam/MediaContainer.git
cd MediaContainer
make setup
```

## API Documentation

### `MediaContainer` (Protocol)

The primary interface for a grouped media container.

- `name` (`str`): The normalized stem identity of the container.
- `files` (`list[ClassifiedFile]`): All files identified as part of this container.
- `video` (`list[ClassifiedFile]`): Ready-to-use video content. Action: `none`.
- `sample` (`list[ClassifiedFile]`): Sample videos (e.g., `-sample.mkv`). Action: `none`.
- `gallery` (`list[ClassifiedFile]`): Sequential image sets. Action: `none`.
- `archives` (`list[ClassifiedFile]`): Archives needing extraction. Action: `extract`.
- `artwork` (`list[ClassifiedFile]`): Covers, screenshots, and other accessory images. Action: `none`.
- `par_files` (`list[ClassifiedFile]`): PAR and PAR2 recovery files. Action: `none`.
- `split_media` (`list[ClassifiedFile]`): Split media files needing stitching. Action: `stitch`.
- `text_files` (`list[ClassifiedFile]`): NFO and TXT files. Action: `none`.
- `nzb` (`list[ClassifiedFile]`): NZB files. Action: `none`.
- `needs_extraction` (`bool`): True if the `archives` list is populated.
- `extraction_tool` (`str | None`): The recommended tool for extraction (`unrar`, `7z`, `unzip`).

### `MediaContainer.from_paths()`

```python
@classmethod
def from_paths(
    cls, 
    paths: list[Path], 
    settings: SettingsProtocol | None = None, 
    logger: LoggingProtocol | None = None
) -> list[MediaContainer]:
```

Classifies and groups a list of filesystem paths into one or more `MediaContainer` instances.

**Parameters:**
- `paths`: A list of `pathlib.Path` objects to process.
- `settings`: (Optional) An object conforming to `SettingsProtocol`.
- `logger`: (Optional) An object conforming to `LoggingProtocol`.

**Returns:**
- A list of `MediaContainer` objects, sorted by relevance (playable content first).

### `ClassifiedFile` (Protocol)

Represents a single file with its metadata extracted from the filename.

- `path` (`Path`): The original path of the file.
- `file_type` (`FileType`): The category of the file (VIDEO, IMAGE, ARCHIVE, etc.).
- `stem` (`str`): The core name of the file after removing all recognized suffixes.
- `qualifier` (`str | None`): Descriptive suffix (e.g., `sample`, `subs`).
- `volume` (`str | None`): Multipart indicator (e.g., `.part1`, `.r00`).
- `extension` (`str`): The file type extension (e.g., `.mkv`).
- `split` (`str | None`): Numeric split suffix (e.g., `.001`).

---

## Data Model

### `FileType` (Enum)

| Value | Description |
|---|---|
| `VIDEO` | Movie and TV show video files. |
| `IMAGE` | Standalone images (covers, posters). |
| `GALLERY` | Sequential image sets (e.g., image001.jpg, image002.jpg). |
| `ARCHIVE` | Single-volume archives (zip, 7z). |
| `MULTIPART_ARCHIVE` | Volumes of a multipart archive (rar, part1.rar). |
| `SPLIT_FILE` | Generic numeric splits (.001). |
| `PAR`, `PAR2` | Parity recovery files. |
| `TEXT` | Metadata and readme files (nfo, txt). |
| `NZB` | Usenet index files. |
| `OTHER` | Unrecognized files. |

---

## Methodology

### Stem Extraction (Right-to-Left Peeling)

Stems are identified by iteratively peeling suffixes from the filename until a base name remains.

1.  **Peel Split**: Removes `.001` through `.999`.
2.  **Peel Volume**: Removes `.partN`, `.rNN`, `.sNN`, and `.volNN+NN`.
3.  **Peel Extension**: Removes known extensions like `.mkv`, `.rar`, `.jpg`.
4.  **Repeat**: Steps 1-3 are repeated in a loop to handle compound suffixes like `.rar.001`.
5.  **Peel Sequence**: Removes trailing digits from image names to identify galleries.
6.  **Strip Qualifier**: Removes recognized descriptive tokens like `-sample` or `_screenshot`.
7.  **Normalize**: Converts to lowercase and replaces word separators (dots, underscores) with spaces.

### Grouping (Longest Common Prefix)

Stems are clustered using a 70% prefix-matching heuristic. Generic accessory names (e.g., `front.jpg`, `cover.png`) are automatically attached to the dominant media group in the directory.

### Scrambled Detection

Files with high-entropy stems (hashes, random strings) of uniform length are grouped together based on their extension patterns rather than their stems.
