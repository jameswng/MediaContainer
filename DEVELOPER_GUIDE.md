# MediaContainer — Developer's Guide

This guide provides a comprehensive reference for developers consuming the `mediacontainer` and `managedsettings` libraries.

---

## 1. ManagedSettings Library (Persistent Configuration)

`ManagedSettings` handles your application's memory-to-disk persistence and configuration merging.

### Core Concepts
- **The `path`**: The disk location (JSON file) for settings. Methods that accept a `path` update the instance's internal default "sticky" path contract.
- **`settings` (Polymorphic)**: Most methods accept a `settings` parameter. This can be either a standard Python `dict` or another object that implements the `SettingsProtocol` (providing an `as_dict()` method).
- **Precedence (`override`)**: 
    - `override=False` (Default): Existing memory keys are preserved; only missing keys are added from incoming data.
    - `override=True`: New incoming data replaces existing memory keys.
- **Argument Precedence**: In any single call where both `path` and `settings` are provided, the **`settings` values always override** the values found in the file.

### API Protocol: `SettingsProtocol`
The library follows a formal Python `typing.Protocol` named `SettingsProtocol`. Any object implementing these methods is compatible.

#### `Settings(path=None, settings=None, override=False)`
**Constructor**.
- **`path`**: Default file address.
- **`settings`**: Initial data to inject (dict or protocol object).
- **`override`**: If `True`, `settings` replaces values loaded from `path`.

#### `get(key, default=None)`
Retrieve a value. Returns `default` if the key is missing.

#### `set(key, value, save=False)`
Update a single setting. 
- **`save`**: If `True`, triggers an immediate `save()` to disk.

#### `load(path=None, settings=None, override=False)`
**Replace memory**. Wipes current settings and loads fresh data from the provided path or source. Updates internal sticky path if provided.

#### `merge(path=None, settings=None, override=False)`
**Combine data**. Adds external data to current memory based on the `override` flag. Updates internal sticky path if provided.

#### `save(path=None, settings=None)`
**Persist to disk**. 
- If `settings` is provided, it is merged into memory (overriding) before writing.
- If `path` is provided, it updates the default address before writing.

#### `as_dict()`
Returns a clone of the internal settings as a standard dictionary.

---

### 2. Implementation Pattern: Cloning & Merging

The polymorphic `settings` parameter makes it easy to work with multiple instances.

```python
from managedsettings import Settings

# 1. Start with system defaults
system_prefs = Settings(settings={"theme": "dark", "volume": 50})

# 2. Create a session instance that starts with system defaults
# but saves to a different file.
session_prefs = Settings(path="~/session.json", settings=system_prefs)

# 3. Merge a simple dictionary
session_prefs.merge(settings={"theme": "high-contrast"}, override=True)
```

---

## 3. MediaContainer Library (Domain Logic)

The core library for identifying and grouping media files.

### Primary API: `MediaContainer`

#### `MediaContainer.from_paths(paths, settings=None)`
Identify and group a list of file paths.

- **Parameters**:
    - `paths` (`list[Path]`): Flat list of paths to classify.
    - `settings` (`SettingsProtocol`): Optional settings object following the protocol.
- **Returns**: A sorted list of `MediaContainer` objects.

---

## 4. Methodology (Internal Logic)

### Stem Extraction
The library uses "Right-to-Left Peeling" to find the core identity of a file by removing splits (`.001`), extensions (`.rar`), and volumes (`.part1`) in sequence.

### longest common prefix Grouping
Stems are clustered by shared starting characters. A shared prefix must represent at least **70%** of the total stem length to be considered a match. Generic files like `front.jpg` are identified as accessories and automatically "glue" to the dominant group.
