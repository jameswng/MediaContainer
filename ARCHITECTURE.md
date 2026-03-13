# MediaContainer — Architecture Document

> Single source of truth for project design. All implementation should follow this document.

## Core Principles (Immutable Mandates)

### 0. The Baseline Principle
All projects MUST inherit and adhere to the Global AI Architecture Baseline. Deviations must be explicitly justified in this document.

### 1. Modern Technical Excellence (Zero-Tolerance)
The codebase must represent the current state of the art in Python development. 
- **Eliminate** all deprecated APIs, obsolete protocols, and legacy design patterns. 
- **Replace** forbidden patterns with modern equivalents immediately.
- **Consolidate** logic into unified, modern paradigms.
- **Python 3.11+**: Utilize modern features like structural pattern matching, advanced type hinting, and `asyncio` where appropriate.
- **Strict Type Annotation**: All functions and methods MUST use PEP 484/526 annotated typing for all parameters and return values.
- **Modern Standards**: Prefer `pathlib` over `os.path`, `pytest` for testing, and `ruff` for linting/formatting.
- **Environment-Clean Safe**: Scripts and execs of script interpreters MUST be environment clean safe and use the appropriate methods to do so (such as `env -i`). They should not rely on the user's personal environment variables (e.g., `PYTHONPATH`, `LD_LIBRARY_PATH`) and MUST use a controlled environment to ensure a predictable execution state. Homebrew bin/sbin directories are considered safe for this context.
    - **Implementation (Python)**: Use `#!/usr/bin/env python3` for binary resolution, followed immediately by an internal `os.environ` pruning block to strip non-essential variables.
    - **Implementation (Shell)**: Use a sentinel-based re-execution pattern: `if [ -z "$CLEANED" ]; then exec env -i ... CLEANED=1 "$0" "$@"; fi`.
- **Developer Special Case**: For development convenience, scripts may use the user's `PATH` via `env` to identify the preferred interpreter (e.g., `python3`), provided the execution environment is otherwise stripped of non-essential variables. This allows the script to respect the user's private path for binary resolution while maintaining a clean execution state.
- **Eliminate Legacy**: No `setup.py`, no old-style classes, no manual string formatting (use f-strings).

### 2. Structural Typing & API Protocols
Public boundaries between modules or libraries MUST be defined by formal interfaces or protocols (e.g., `typing.Protocol`). Avoid tight coupling to concrete classes. This ensures structural typing and prevents circular dependencies.

### 3. Dual Summary Architecture (Automated & Continuous Logging)
The project MUST maintain two distinct summary files to balance context efficiency with historical traceability:
- **`SESSION_SUMMARY.md`**: High-signal, overwritable summary. Contains only the *current* architectural truth and the accomplishments of the *latest* session. **Crucially, this relies on an "on-the-fly summarization" principle:** it MUST be updated continuously during a session (not just at the end) to prevent context loss in the event of an accidental crash. Tracked by Git, read by AI.
- **`FULL_SESSION_SUMMARY.md`**: High-density historical log. An append-only document that captures every accomplishment from project inception in **meaningful prose**. This file MUST be ignored by context-loading routines (e.g., added to BOTH `.claudeignore` and `.geminiignore`) to prevent context bloat but MUST be tracked by Git.
    - **NO DIFFS/CODE**: Raw code blocks, diffs, and noisy terminal output are strictly forbidden.
    - **RECOMPOSITION**: Technical details are preserved via the Git history and retrieved using `bin/recompose_history.py`.

### 4. Automated Continuous Versioning
The project MUST use a Semantic Versioning (SemVer) strategy. The **Patch** version (e.g., 1.0.x) MUST be automatically advanced by the build system (e.g., `Makefile` target `test` or `checkpoint`) every time a change is compiled or tested, ensuring perfect traceability.

### 5. Self-Documenting Source Headers
Every source file MUST begin with a comprehensive header block that details:
- **Calling API**: The intended interface and external dependencies.
- **Algorithmic Methodology**: The logic or mathematical approach used (e.g., natural sorting, pipe chaining).
- **Program Flow**: A high-level trace of how the file executes from entry to exit.

### 6. Living Developer's Guide
The project MUST maintain a `DEVELOPER_GUIDE.md` that serves as the primary onboarding and reference document for library consumers. It MUST contain:
- **Installation**: Clear instructions for setting up the library.
- **API Documentation**: A complete reference of all exposed APIs and protocols for the core library AND any support libraries.
    - Each entry MUST include a detailed explanation of parameters, return values, and intended usage.
    - For complex cases or advanced features, a suitable, runnable example MUST be provided.
- **Data Model**: Exhaustive detail on public classes, attributes, and enums.
- **Methodology**: Explanation of the core algorithms (grouping, classification) from a consumer's perspective.

### 7. Isolated System Boundaries & Environment-Clean Execution
Maintain strict separation of concerns and runtime predictable state:
- **Self-Locating Executables**: Binaries and scripts must dynamically resolve their own paths rather than relying on the caller's working directory.
- **Standardized Discoverability**: Any command that can be run standalone MUST provide a `-h` or `--help` option detailing its usage (`Makefile`s MUST provide a `help` target).

### 8. Comprehensive Validation & Initialization
A robust build system must standardize the development lifecycle.
- **Target `setup`**: Initializes the environment (e.g., dependencies).
- **Target `test`**: Executes the test suite (depends on `setup`). All source files should be unit tested, leveraging inherent mockability.
- **Target `lint`**: Executes static analysis.
- **Target `format`**: Automatically applies standard code formatting (e.g., `ruff format`).
- **System Logging**: All critical errors must be reported to the native system logger (`syslog`, `os_log`) out-of-band.

### 9. "Shadow WIP" State Management & Deterministic Checkpoints
AI workflows require frequent saving of intermediate progress.
- **Target `wip`**: Safely stashes current progress by creating or amending a `WIP: Intermediate state` commit, acting as an invisible safety net without cluttering the Git log.
- **Target `checkpoint` / `commit`**: Chains the `version-advance` logic, finalizes the Git commit history with a clean, semantic label, and **MUST** push the resulting state to the remote repository (e.g., GitHub) to guarantee off-site backup.
- **Mandatory Finalization**: Before ending a session or starting a new one (`/new`), the agent MUST verify if a `Checkpoint` was made. If not, a `Quickcheck` (doc update + push) MUST be performed.

### 10. The Unblocked User & Native Platform Parity
Application responsiveness and native integration are paramount.
- **Performance First**: No action may block the primary user thread. Everything must be asynchronous, provide instant feedback, and prioritize minimizing I/O.
- **Native Visuals**: Comply strictly with native Human Interface Guidelines (HIG).
- **Native Behavior**: Emulate native OS behaviors exactly (e.g., standard keyboard shortcuts, native sorting logic).

### 11. Operational Targets & Deterministic Purging
The `Makefile` should expose standard operational verbs:
- **Targets `build` / `install` / `start` / `stop`**: Manage the lifecycle of compiled artifacts and services.
- **Target `clean`**: Executes focused deletions on known temporary directories to return the project to a pristine baseline. Crucially, **tracked session files** must NOT be purged.

---

## Automation & Environment Standards

### Clean Shell
Every shell invocation MUST start with no profile or rc files loaded. Use `/bin/bash --noprofile --norc`. Bare `bash`, `zsh`, and `/bin/sh` are forbidden in automation contexts.

### Strict PATH
The execution environment is restricted to a set of known-safe system and package manager directories:
`/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin`

No additional directories (like user-local `bin` or project-relative paths) are permitted in the base execution `PATH`. `export PATH` must be set explicitly in the `Makefile` and any automation scripts.

---

## Support Libraries

To maintain a clean and decoupled domain model, generic infrastructure tasks (such as configuration management) are handled by dedicated support libraries residing in the same workspace.

### ManagedSettings (SettingsProtocol)
A standalone, dictionary-backed persistence library following a formal `typing.Protocol` named `SettingsProtocol`.
- **Explicit Path Control**: Methods accepting a `path` argument MUST include a `set_path: bool = False` flag. The internal default path is only updated if `set_path` is `True`.
- **Polymorphic Input**: All data parameters (named `settings`) accept either a standard Python `dict` or another `SettingsProtocol` object.
- **Loading vs. Merging**:
    - `load()`: Clears existing in-memory settings before applying new data.
    - `merge()`: Combines new data with existing settings.
- **The Contract**: Beyond the formal protocol, the library follows an API contract where the instance maintains a "sticky" path for its lifetime once set.
- **Precedence (Override)**: Merging operations use an `override` flag (default: `False`) to determine if incoming keys replace existing ones.
- **Exportable**: The library provides an `as_dict()` method to allow cloning or external processing of the raw settings.

---

## Purpose

Scan a directory, identify which files belong together as logical "media containers," extract any archives, and play the resulting media.

## Core Problem

Files in a directory may form one or more **media containers**. The rules for grouping files are fluid and not always straightforward. A media container may contain any combination of:

- Video files
- Image files (cover art, screenshots, or image sets/galleries)
- Archive files (rar, zip, 7z)
- Multipart archive volumes (rar/r00–r99, part1.rar/part2.rar)
- Split files (generic numeric splits: name.ext.001, name.ext.002)
- Par/par2 files
- Text files (txt, nfo)
- NZB files
- Any other file with a similar stem

Files are related by naming convention, but the conventions vary. Examples:
- `Release_Name.rar`, `Release_Name.r00`, `Release_Name.r01` — obvious match
- `Release_Name.rar`, `Release_Name_screenshot.jpg` — related by shared prefix
- `front.jpg`, `back.jpg`, `screen.jpg` — generic accessory names, belong to the dominant media container
- `flowers_01.jpg`, `flowers_02.jpg`, ... — image set media container

Usually there is one media container per directory, but not always.

---

## MediaContainer Module

**Standalone library module, decoupled from extraction and playback. Importable by other apps.**

### Interface

```python
class MediaContainer:
    name: str
    files: list[ClassifiedFile]

    @classmethod
    def from_paths(cls, paths: list[Path]) -> list[MediaContainer]:
        """Accept a list of Paths, classify and group them,
        return one or more MediaContainer instances."""
```

- **Input:** a list of Path objects
- **Output:** a list of `MediaContainer` instances, each containing its affiliated `ClassifiedFile` entries
- Initial classification and grouping uses filenames only (pure string logic)
- **Filesystem access on demand:** for outlier resolution the module may access the filesystem to inspect file headers or sizes
- **Importable as a library** by other apps

### Filename Anatomy

A filename is decomposed into named parts during classification:

```
stem-sample.part1.rar.001
│          │      │    │   └── split: numeric split suffix (.001–.999)
│          │      │    └────── extension: file type extension (.rar)
│          │      └─────────── volume: multipart indicator (.part1, .r00, .vol0+1)
│          └────────────────── qualifier: descriptive suffix (sample, screenshot, subs)
└───────────────────────────── stem: the core identity used for grouping
```

**Terminology:**
- **stem** — the core name after all suffixes are removed; used for grouping
- **qualifier** — a descriptive suffix attached to the stem (e.g., `-sample`, `_screenshot`)
- **volume** — multipart/volume indicator (e.g., `.part1`, `.r00`, `.vol0+1`)
- **extension** — file type extension (e.g., `.rar`, `.avi`, `.jpg`)
- **split** — numeric split suffix (e.g., `.001`, `.002`)

### File Classification

Each filename is classified by extension into a `FileType`:

- VIDEO: .avi, .mkv, .mp4, .m4v, .wmv, .flv, .mov, .mpg, .mpeg, .ts, .vob, .ogm, .divx, .webm
- IMAGE: .jpg, .jpeg, .png, .bmp, .gif, .tif, .tiff, .webp
- ARCHIVE: .rar, .zip, .7z
- MULTIPART_ARCHIVE: .r00–.r99, .s00–.s99, part1.rar/part2.rar (volumes of a multipart archive set)
- SPLIT_FILE: .001–.999 numeric splits — meaning depends on context (see Split File Context Rules)
- PAR: .par
- PAR2: .par2, .vol0+1.par2
- TEXT: .txt, .nfo
- NZB: .nzb
- OTHER: anything else — still grouped by stem affiliation

### Stem Extraction

Iterative right-to-left peeling of recognized suffixes until none remain:

**Peel rules** (applied in a loop until no more match):
- Split: `.001`–`.999`
- Volume: `.r00`–`.r99`, `.s00`–`.s99`, `.partN`, `.part01`, `.part001`, `.vol0+1` etc.
- Extension: `.rar`, `.zip`, `.7z`, `.avi`, `.mkv`, `.mp4`, `.jpg`, `.par2`, `.txt`, `.nfo`, `.nzb`, etc.

**Strip rules** (applied once after peeling):
- Qualifier: `sample`, `screenshot`, `subs`, `proof`, `covers`

**Normalize:**
- Lowercase
- Replace dots and underscores with spaces (preserve hyphens)

**Examples:**
```
stem.avi.001          → peel .001 (split) → peel .avi (ext)       → stem: "stem"
stem.rar.001          → peel .001 (split) → peel .rar (ext)       → stem: "stem"
stem.part1.rar        → peel .rar (ext) → peel .part1 (volume)    → stem: "stem"
stem.r00              → peel .r00 (volume)                         → stem: "stem"
stem.vol0+1.par2      → peel .par2 (ext) → peel .vol0+1 (volume)  → stem: "stem"
stem-sample.avi       → peel .avi (ext) → strip -sample (qual)     → stem: "stem"
stem_screenshot.jpg   → peel .jpg (ext) → strip _screenshot (qual) → stem: "stem"
front.jpg                 → peel .jpg (ext)                             → stem: "front" (accessory)
stem.nzb              → peel .nzb (ext)                             → stem: "stem"
```

### Grouping Algorithm

**Core assumption:** All files sharing a stem or similar stem are affiliated.

1. Compute normalized stem for every file.
2. Group by **longest common prefix** (the longest string that two or more stems share from the start) on normalized stems. This handles the majority of cases (95–99% accuracy target).
3. For difficult cases where longest common prefix is insufficient, apply secondary heuristics (e.g., SequenceMatcher similarity). Edge cases will be addressed as they occur — 100% accuracy is not a goal.
4. Generic accessory names (`front.jpg`, `back.jpg`, `cover.jpg`, `index.jpg`, etc.) attach to the dominant group. These can appear in any type of media container — video releases, image sets, etc.
5. If only one group emerges, treat everything as one media container.
6. **Image sets** are media containers like any other. They may include their own accessory files (front, back, cover, index, clean versions, etc.).
7. Files that cannot be affiliated with any group go into a single catch-all **unaffiliated** media container.

**Known accessory names:** front, back, cover, screen, screens, screenshot, folder, poster, thumb, fanart, banner, disc, disk, index, clean

### List Assignment

Once files are grouped into a media container, each file is sorted into the appropriate content list (playable, sample, artwork, archives, etc.) based on:

- **Filename** — qualifiers (e.g., `-sample` → sample list), known accessory names (e.g., `front.jpg` → artwork list), file type/extension
- **File size** — may be used to distinguish sample from playable (e.g., a small video alongside a large one)
- **No filesystem content inspection** for list assignment

### Scrambled Filename Detection

When stems cannot be grouped by longest common prefix or similarity because they are obfuscated (hashes, random strings), detect and group by extension pattern instead.

**Detection criteria** (all must be true for a cluster of files):
- Stems are all the **same length**
- Stems use a **restricted, uniform alphabet** (e.g., hex: 0-9a-f, or base64, or alphanumeric-only)
- Stems lack typical naming structure (no word separators, no recognizable tokens)
- Multiple files match this pattern (a single random-looking name is not enough)

**Grouping rule:** When a set of files is detected as scrambled, ignore stems and group by extension pattern. E.g., a collection of `.r00`–`.r99` files with hash stems forms one multipart archive container.

**Example:**
```
bc3eed3e69df...e1.r88    ─┐
bd827022004a...a6.r32     │
c01ae13de93e...91.r64     ├── all hex stems, same length, .rNN extensions
e382220a8393...7c.r00     │   → one multipart archive media container
f120a88beea0...33.r36    ─┘
```

### Split File Context Rules

The meaning of `.001`/`.002` numeric split files depends on what they're splitting:

| Pattern | Interpretation |
|---|---|
| `name.rar.001`, `name.rar.002` | Split archive (rar) |
| `name.zip.001`, `name.zip.002` | Split archive (zip) |
| `name.7z.001`, `name.7z.002` | Split archive (7z) |
| `movie.avi.001`, `movie.avi.002` | Split media file |
| `name.001`, `name.002` (no known ext before split) | Ambiguous — heuristic needed |

### Data Model

**ClassifiedFile:** path (Path), file_type (FileType), stem (str), qualifier (str|None), volume (str|None), extension (str), split (str|None)

**MediaContainer:**

Content:
- **name** — the container's stem identity
- **files** — all files in the container (flat list)
- **playable** — videos, main playable content (action: none)
- **sample** — sample video(s) (action: none)
- **artwork** — front, back, cover, screenshots, etc. (action: none)
- **archives** — all archive/multipart files (action: extract)
- **primary_archive** — the entry point file for extraction (see Primary Archive Selection)
- **par_files** — par/par2 files (action: none)
- **split_media** — split media files needing stitching (action: stitch)
- **text_files** — nfo, txt (action: none)
- **nzb** — nzb files (action: none)
- **misc** — everything else (action: none)

Each content list has an implicit **action_needed** (noted in parentheses above). The consumer checks which lists are populated and what actions they require.

Computed:
- **extraction_tool** — which tool to invoke if extraction is needed (unrar, 7z, unzip, or None)

Flags:
- **scrambled** — filenames are obfuscated
- **incomplete** — primary archive missing, or last split file is the same size as all others (more data expected)
- **corrupted** — split files have inconsistent sizes (all should be equal except possibly the last)
- **unaffiliated** — catch-all container for files that couldn't be grouped and aren't a recognized valid type on their own

### Action Needed

Action is a per-content-list attribute, not per-container. Each list implies what processing is required:

| Content list | action | Meaning |
|---|---|---|
| playable, sample, artwork, par_files, text_files, nzb, misc | `none` | Directly accessible |
| archives | `extract` | Must be extracted |
| split_media | `stitch` | Must be concatenated |

A container with both `playable` and `archives` populated has content at different readiness levels — some ready, some needing work. The consumer handles each accordingly.

Note: `stitch+extract` applies when split files reassemble into an archive (e.g., `name.rar.001`) — the consumer stitches first, then extracts.

### Extraction Tool

Derived from the primary archive's extension:

| Primary archive | extraction_tool |
|---|---|
| `.rar` | unrar |
| `.zip` | unzip or 7z |
| `.7z` | 7z |
| `.rar.001` | TBD (needs testing) |
| `.zip.001` | TBD (needs testing) |
| `.7z.001` | 7z |

### Primary Archive Selection

The primary archive is the file a tool would be invoked on to begin extraction:

| Archive type | Primary file |
|---|---|
| rar + r00–r99 | the `.rar` file |
| partN.rar series | `part1.rar` (or `part01.rar`) |
| Numeric split (.001) | the `.001` file |
| Single .zip or .7z | that file |

If no primary archive can be identified in an archive-based container, flag as **incomplete**.

### Archive Health (file size heuristics)

For split/multipart archives, file sizes provide health signals:

- **Complete**: last split is smaller than the others (normal — final chunk is a partial)
- **Incomplete**: last split is the same size as all others (more data expected), or primary archive is missing
- **Corrupted**: split files have inconsistent sizes (all should be equal except possibly the last)

### Ordering

- **Archives/splits**: ordered by volume/split number
- **Playable files**: ordered by name (handles CD1/CD2 naturally)

### Container Assignment Rules

- A file with a recognized valid type (video, image, archive, etc.) always gets a proper container, even if it's the only file
- Files that can't be affiliated with any group *and* aren't a recognized valid type go into the single **unaffiliated** catch-all container
- Empty input returns an empty list

---

## Deferred

Everything below is outside the MediaContainer module and deferred to future implementation.

### Nested Archives
Archives may contain other archives (e.g., zip files containing rar files, or rar files containing a broken/split rar set). MediaContainer cannot detect this — it only sees filenames in a directory, not archive contents. The consumer can handle this iteratively: extract, run `from_paths()` on the extracted contents, repeat if more archives are found. May be formalized as a built-in pattern in the future.

### Extraction / Stitching
- Multipart archive extraction (unrar, 7z, zip)
- Split media file stitching (concatenation)
- Ram drive (`/Volumes/ram`) — required for extraction and stitching, no fallback

### Playback
- Launch media player (likely mpv) with extracted/loose media files
- Image viewer for image-set containers
- CD1/CD2 ordering
- Do not play container metadata files (archives, par, nfo, nzb)

### Environment
- Ram drive detection and space checking

### Visual Analysis
For outlier grouping disambiguation when filename-based heuristics are insufficient. Possible approaches:

- **Perceptual hashing** (pHash, dHash): generates a compact fingerprint per image/frame. Similar visuals produce similar hashes, compared via hamming distance. Fast and lightweight.
- **Color histogram correlation**: compute RGB/HSV histograms, compare distributions. Good for detecting images from the same shoot or scene.
- **Dominant palette extraction**: k-means clustering on pixel colors. Useful for "same photo set" detection.
- **Keyframe extraction** (video): pull a few frames (first, middle, end) via ffmpeg, then apply any of the above image techniques to compare videos.
- **Average luminance/contrast**: coarse but cheap — compare mean brightness and standard deviation across images.

### Declarative Rule Configuration
Extract hardcoded stem peeling/stripping rules into a configurable, declarative format. Possible approaches:

- **Config-driven rules**: define peel/strip patterns in YAML, TOML, or a Python dict. A generic processor iterates and applies them.
- **Ordered rule chains**: rules have priority/ordering, processor applies them right-to-left on the filename until no more match.
- **Per-app overrides**: consuming apps can inject custom rules without modifying the core rule set.

## Module Structure

```
mediacontainer/
├── __init__.py         — library exports
├── media_container.py  — MediaContainer class (standalone library)
└── settings.py         — persistent settings/preferences management
```

Future modules (deferred):
```
├── extract.py          — archive extraction, split stitching
├── player.py           — media playback orchestration
└── cli.py              — CLI entry point
```
