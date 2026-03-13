# MediaContainer — Developer's Guide

This guide provides a comprehensive reference for developers consuming the `mediacontainer`, `managedsettings`, and `sysloglogger` libraries within this workspace.

## 1. Installation & Environment

The workspace provides isolated, standard environments and tasks managed via `make`.

- `make setup`: Initializes the environment and installs dependencies.
- `make test`: Executes the test suite via `pytest`.
- `make lint`: Executes static analysis via `ruff`.
- `make format`: Automatically applies code formatting.

All binaries and scripts in this project are **Environment-Clean Safe**; they dynamically resolve their paths and strip user-local variables to ensure deterministic execution environments.

---

## 2. ManagedSettings (SettingsProtocol)

A standalone, persistent configuration library.

### Core Concepts
- **Explicit Path Control**: Methods accepting a `path` parameter will only update the instance's "sticky" internal path if `set_path=True` is provided.
- **Polymorphic Input**: The `settings` parameter accepts either a standard Python `dict` or another object implementing the `SettingsProtocol` (providing `as_dict()`).
- **Precedence (`override`)**: 
    - `override=False` (Default): Existing memory keys are preserved.
    - `override=True`: New incoming data replaces existing memory keys.
- **Dependency Injection**: Can accept a `LoggingProtocol` compliant object to handle non-blocking error reporting.

### Implementation Example

```python
from managedsettings import Settings
from sysloglogger import log_error, log_info, log_warning

class SysLogger:
    def log_error(self, ident: str, msg: str) -> None: log_error(ident, msg)
    def log_info(self, ident: str, msg: str) -> None: log_info(ident, msg)
    def log_warning(self, ident: str, msg: str) -> None: log_warning(ident, msg)

logger = SysLogger()

# Initialize with logger
session_prefs = Settings(path="~/session.json", logger=logger)

# Merge dict explicitly, update the default path
session_prefs.merge(path="~/new_session.json", set_path=True, settings={"theme": "dark"})
```

---

## 3. SyslogLogger Library

A standalone, zero-dependency package providing native system logging.

### API
- `log_error(ident: str, message: str)`
- `log_warning(ident: str, message: str)`
- `log_info(ident: str, message: str)`

**Usage:**
```python
import sysloglogger

sysloglogger.log_info("myapp", "Application started gracefully.")
```

---

## 4. MediaContainer Library (Domain Logic)

The core domain model, cleanly decoupled from external concerns.

### Primary API: `MediaContainer`

#### `MediaContainer.from_paths(paths, settings=None, logger=None)`
Identify and group a list of file paths.

- **Parameters**:
    - `paths` (`list[Path]`): Flat list of paths to classify.
    - `settings` (`SettingsProtocol` | None): Optional injected configuration object.
    - `logger` (`LoggingProtocol` | None): Optional injected logging object.
- **Returns**: A sorted list of `MediaContainer` objects.

### Data Model & Output Protocols

When you invoke `MediaContainer.from_paths()`, the resulting data conforms to strictly typed protocols defined in the codebase. 

#### 1. `ClassifiedFileProtocol`
Each file scanned by the system is decomposed into a `ClassifiedFile` object, which exposes the exact anatomical breakdown of the filename:
- `path` (`Path`): The original path of the file.
- `file_type` (`FileType` Enum): A defined category (e.g., `FileType.VIDEO`, `FileType.ARCHIVE`, `FileType.SPLIT_FILE`).
- `stem` (`str`): The core normalized identity of the file used for clustering.
- `qualifier` (`str | None`): Any descriptive suffix stripped from the stem (e.g., `"sample"`, `"screenshot"`).
- `volume` (`str | None`): The archive volume string if present (e.g., `".part1"`, `".r00"`).
- `extension` (`str`): The primary recognized extension (e.g., `".rar"`, `".mkv"`).
- `split` (`str | None`): The numeric split suffix if present (e.g., `".001"`).

#### 2. `MediaContainerProtocol`
The main return objects (containers) expose a rich set of lists to safely handle their specific execution actions.

- `name` (`str`): The normalized stem identity of the container.
- `files` (`list[ClassifiedFile]`): Flat list of *all* files assigned to the container.

**Action Contexts (Categorized Lists):**
- `playable` (`list[ClassifiedFile]`): Ready-to-use playable content (e.g., videos). Action: `none`.
- `archives` (`list[ClassifiedFile]`): Standard and multipart archives. Action: `extract`.
- `split_media` (`list[ClassifiedFile]`): Raw split files (e.g., `.avi.001`). Action: `stitch`.
- **Supporting Lists:** `artwork`, `par_files`, `text_files`, `nzb`, `sample`, `misc`.

**Computed Properties (Resolution logic):**
- `primary_archive` (`ClassifiedFile | None`): The definitive entry-point file for extraction tools (e.g., finding the exact `.rar` file amidst a sea of `.r00` files).
- `extraction_tool` (`str | None`): The CLI utility required for this container (returns `"unrar"`, `"7z"`, `"unzip"`, or `None`).

**Health Flags:**
- `scrambled` (`bool`): True if the container stems were obfuscated/hashed (e.g., Usenet obfuscation).
- `incomplete` (`bool`): True if the container has archives but is missing its `primary_archive` entry-point.
- `unaffiliated` (`bool`): True for the catch-all container of unmatched outlier files.

---

## 5. Methodology (Internal Logic)

### Stem Extraction (Right-to-Left Peeling)
The library isolates the core identity of a file by iteratively removing structural suffixes:
1. Splits (`.001`)
2. Volumes (`.r00`, `.part1`)
3. Standard Extensions (`.rar`, `.mkv`)
4. Finally stripping trailing qualifiers (`-sample`, `_screenshot`).

### Longest Common Prefix Grouping
Stems are clustered by their shared starting characters. A match generally requires a shared prefix length of at least **70%** of the total stem size. 

Generic files (like `front.jpg`) are mapped as accessories and automatically attach themselves to the dominant media container within the directory, regardless of their lack of stem similarity.

### Scrambled Heuristics
If filenames are obfuscated (e.g., pure hexadecimal strings of identical length), the standard longest-common-prefix heuristic is bypassed, and the library automatically regroups the files based on contiguous extension blocks (like a full `.r00` to `.r99` sequence).
