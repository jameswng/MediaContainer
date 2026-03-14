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

Files are related by naming convention, but the conventions vary.

---

## Module-Specific Architectures

To maintain a clean and decoupled domain model, detailed implementation logic is contained within module-specific architecture files:

- **[MediaContainer Module](mediacontainer/ARCHITECTURE.md)**: Logic for file grouping, classification, stem parsing, and visual analysis.
- **[ManagedSettings Module](managedsettings/ARCHITECTURE.md)**: Logic for dictionary-backed configuration and persistence.
- **[SyslogLogger Module](sysloglogger/ARCHITECTURE.md)**: Logic for out-of-band system logging.
