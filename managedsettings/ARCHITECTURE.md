# ManagedSettings Architecture

## Core Principles (Inherited from Project Root)

### 0. The Baseline Principle
All projects MUST inherit and adhere to the Global AI Architecture Baseline.

### 1. Modern Technical Excellence
- **Python 3.11+**: Utilize modern features like structural pattern matching and advanced type hinting.
- **Strict Type Annotation**: All functions and methods MUST use PEP 484/526 annotated typing.
- **Modern Standards**: Prefer `pathlib` over `os.path`.
- **Eliminate Legacy**: No old-style classes, no manual string formatting (use f-strings).

### 2. Structural Typing & API Protocols
Public boundaries MUST be defined by formal interfaces or protocols (`typing.Protocol`).

### 5. Self-Documenting Source Headers
Every source file MUST begin with a comprehensive header block detailing Calling API, Algorithmic Methodology, and Program Flow.

---

## ManagedSettings (SettingsProtocol)

A standalone, dictionary-backed persistence library following a formal `typing.Protocol` named `SettingsProtocol`.

### Design Mandates
- **Explicit Path Control**: Methods accepting a `path` argument MUST include a `set_path: bool = False` flag. The internal default path is only updated if `set_path` is `True`.
- **Polymorphic Input**: All data parameters (named `settings`) accept either a standard Python `dict` or another `SettingsProtocol` object.
- **Loading vs. Merging**:
    - `load()`: Clears existing in-memory settings before applying new data.
    - `merge()`: Combines new data with existing settings.
- **The Contract**: Beyond the formal protocol, the library follows an API contract where the instance maintains a "sticky" path for its lifetime once set.
- **Precedence (Override)**: Merging operations use an `override` flag (default: `False`) to determine if incoming keys replace existing ones.
- **Exportable**: The library provides an `as_dict()` method to allow cloning or external processing of the raw settings.
