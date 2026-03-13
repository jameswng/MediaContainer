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
    stem: str
    lcp: str  # alias to stem
    files: list[ClassifiedFile]

    @classmethod
    def from_paths(cls, paths: list[Path]) -> list[MediaContainer]:
        """Accept a list of Paths, classify and group them,
        return one or more MediaContainer instances."""
```

- **Input:** a list of Path objects
- **Output:** a list of `MediaContainer` instances, each containing its affiliated `ClassifiedFile` entries
- Initial classification and grouping uses filenames only (pure string logic)
- **Visual Analysis Fallback**: for cases where filename heuristics are insufficient (e.g., `1.jpg`, `2.jpg`), the module performs macOS native visual fingerprinting to identify logical sets.
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
- **stem** — the normalized core name (lowercase, space-separated) used for grouping
- **raw_stem** — the unmodified core name string after suffix/sequence removal
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

### Stem Extraction (Rule-based Parser DSL)

Stems are identified by a declarative `Parser` that applies a set of ordered rules to the filename. 

**Rule Configuration (`baked-in-rules.json`):**
Rules are defined in an external JSON file. Simple rules use regex `pattern`, while complex logic uses `function` placeholders that call internal parser methods.

**Rule Types:**
- **Peel**: Extracts a value (e.g., volume, split, sequence) and removes it from the filename string.
- **Strip**: Removes recognized descriptive tokens (e.g., qualifiers) from the filename string.

**Scopes:**
- **Suffix**: The rule only matches if the pattern occurs at the end of the current filename (applied iteratively right-to-left).
- **Global**: The rule matches anywhere in the stem (used for mid-string sequences or custom tags).

**Baseline Rule Priority (Processed in order):**
1.  **Split**: `.001` through `.999` (Suffix)
2.  **Volume**: `.partN`, `.rNN`, `.sNN`, `.volNN+NN` (Suffix)
3.  **Extension**: Known media and archive extensions (Suffix)
4.  **Qualifier**: `sample`, `subs`, etc. (Suffix Strip)
5.  **Heuristic Sequence**: Complex mid-string sequence extraction (Global Function)

**Normalization:**
After rules are applied, the remaining string is normalized:
- Lowercase
- Replace word separators (dots, underscores, brackets) with spaces
- **Preserve Hyphens**: hyphens are treated as part of the stem (e.g., `release-grp`)
- Trim whitespace and collapse multiple spaces

---

## Configuration Engine

`MediaContainer` uses a hybrid configuration model to manage the variety of filename combinations.

### 1. Default Baseline (`baked-in-rules.json`)
The core library loads rules from `baked-in-rules.json`. This provides industry-standard handling of Scene rules, multipart archives, and common gallery formats.

### 2. Declarative DSL (`parser_rules`)
Users and applications can extend or override the baseline behavior via the `parser_rules` key in the global settings (`~/.mediacontainer.json`). 

**Configuration Schema (JSON):**
```json
{
  "parser_rules": [
    {
      "name": "rule_name",
      "pattern": "regex_string",
      "action": "peel | strip",
      "scope": "suffix | global"
    }
  ]
}
```
Custom rules are prepended to the baseline set, giving them highest priority.

---

## Grouping Algorithm

**Core assumption:** All files sharing a stem or similar stem are affiliated.

1.  **Longest Common Prefix**: Cluster files by normalized stems.
2.  **Visual Clustering**: For "weak" groups (empty, numeric, or single-character stems), perform visual analysis on images.
3.  **Accessory Attachment**: Generic accessory names (`front.jpg`, etc.) attach to the dominant group.
4.  **Catch-all**: Unaffiliated files go into an "unaffiliated" container.

### Visual Analysis (Darwin/macOS)

For image sets with non-descriptive names (e.g. `1.jpg`, `2.jpg`), the module utilizes macOS `sips` to generate visual fingerprints and histograms.

**Grouping Strategies:**
1.  **Structural Match (Average Hash)**: 
    - Images are downsampled to 8x8 pixels.
    - A 64-bit string is generated where each bit represents whether a pixel is above or below the average brightness.
    - Hamming distance ≤ 10 indicates a structural match (good for resizing).
2.  **Pictorial Match (Color Histogram)**:
    - Images are downsampled to 32x32 pixels.
    - A 125-bin normalized color histogram is generated (5 levels per RGB channel).
    - Cosine similarity (correlation) ≥ 0.95 indicates a pictorial match (good for crops or related photos from the same pictorial/scene).

### Container Naming (Maximal Readable Name)

The `MediaContainer.name` is derived from the **unmodified Longest Common Prefix (LCP)** of the grouped files' `raw_stem` attributes.

**Naming Algorithm:**
1.  **Extract LCP**: Calculate prefix of `raw_stem` strings.
2.  **Dominant Separator**: Identify the most frequent separator (`.`, `_`, or `-`) in the LCP.
3.  **Cleanup**: Remove brackets, strip non-alphanumeric chars.
4.  **Normalization**: Replace internal whitespace/separators with the dominant separator.
5.  **Fallback**: If the LCP is empty/weak, use a generated name like `[Gallery-HASH]`.

**Resultant Attributes:**
- `stem`: The raw, unmodified longest common prefix.
- `lcp`: Alias to `stem`.
- `name`: The "Maximal Readable Name" generated by the algorithm above.

### CLI Display (Gallery Summarization)

To maintain a high-signal output, the CLI summarizes sequential image sets (galleries) by default. Instead of listing every image, it displays a pattern where digits are replaced by hashes (`#`).

- **Standard/Verbose Mode (`-v`)**: Displays `gallery: [ 'stem##.type' ]`.
- **Extra Verbose Mode (`-vv`)**: Displays the full, explicit list of files within the gallery.

---

## Module Structure

```
mediacontainer/
├── __init__.py         — core library exports
├── media_container.py  — MediaContainer logic
├── parser.py           — Rule-based filename parser
├── visual.py           — macOS native visual analysis
└── baked-in-rules.json — baseline parsing DSL
```

---

## Deferred

Everything below is outside the core MediaContainer library and deferred to future implementation.

### Nested Archives
Archives may contain other archives (e.g., zip files containing rar files). The consumer can handle this iteratively: extract, run `from_paths()` on the extracted contents, and repeat.

### Extraction Orchestration
- Multipart archive extraction (unrar, 7z, zip) using the identified `extraction_tool`.
- Split media file stitching (concatenation).

### Visual Analysis (AI-Powered)
For extremely ambiguous image sets, the library aims to leverage small Vision Language Models (VLMs) for semantic grouping.

**Target Model: Moondream2 (1.6B)**
- **Size**: 1.6 Billion parameters (the smallest realistic floor for high-quality vision understanding).
- **Resources**: Requires ~2-3GB of RAM/VRAM. Optimized for CPU execution and Apple Silicon (Metal).
- **Functional Goal**:
    1. **Semantic Captioning**: Generate a one-sentence description for every image in a "weak" group.
    2. **Text Similarity Clustering**: Group images whose AI-generated captions share high semantic similarity (e.g., "A photo of a red sports car" and "Side profile of a red vehicle").
- **Integration Paths**:
    - **Native Python**: Utilizing the `transformers`, `einops`, and `pillow` libraries for direct in-process execution.
    - **Ollama API**: Utilizing a local Ollama instance for out-of-process inference via a REST API.
