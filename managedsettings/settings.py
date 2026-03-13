"""
# ManagedSettings — Implementation of Persistent Settings Protocol

## Calling API
- `Settings(path: Path | str | None = None, settings: dict | SettingsProtocol | None = None, override: bool = False)`
- `get(key: str, default: Any = None) -> Any`
- `set(key: str, value: Any, save: bool = False) -> None`
- `load(path: Path | str | None = None, settings: dict | SettingsProtocol | None = None, override: bool = False, set_path: bool = False) -> None`
- `save(path: Path | str | None = None, settings: dict | SettingsProtocol | None = None, set_path: bool = False) -> None`
- `merge(path: Path | str | None = None, settings: dict | SettingsProtocol | None = None, override: bool = False, set_path: bool = False) -> None`
- `as_dict() -> dict[str, Any]`: Returns a clone of the internal settings dictionary.

## Algorithmic Methodology
- **SettingsProtocol**: Formal PEP 544 Protocol for structural typing.
- **Explicit Path Control**: Internal path only updates in methods if `set_path` is True.
- **Polymorphic Input**: Data parameters accept either `dict` or `SettingsProtocol` objects.
- **Precedence (Arguments)**: In any single call, `settings` values override `path` file values.
- **Precedence (State)**: The `override` flag (default: `False`) determines if incoming data replaces existing memory.

## Program Flow
1. Initialize storage and the primary path.
2. Handle polymorphic input.
3. Apply merging/loading logic based on precedence rules.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SettingsProtocol(Protocol):
    """Formal protocol defining the expected interface for settings management."""
    path: Path | None

    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any, save: bool = False) -> None: ...
    def load(self, path: Path | str | None = None, settings: dict[str, Any] | SettingsProtocol | None = None, override: bool = False, set_path: bool = False) -> None: ...
    def save(self, path: Path | str | None = None, settings: dict[str, Any] | SettingsProtocol | None = None, set_path: bool = False) -> None: ...
    def merge(self, path: Path | str | None = None, settings: dict[str, Any] | SettingsProtocol | None = None, override: bool = False, set_path: bool = False) -> None: ...
    def as_dict(self) -> dict[str, Any]: ...


class Settings:
    """
    A managed key-value store with JSON persistence and explicit path management.
    Implements the SettingsProtocol.
    """

    def __init__(
        self, 
        path: Path | str | None = None, 
        settings: dict[str, Any] | SettingsProtocol | None = None, 
        override: bool = False
    ):
        self._data: dict[str, Any] = {}
        self.path: Path | None = Path(path).expanduser().resolve() if path else None
        
        # Initial load logic: Memory starts empty.
        # We pass self.path to merge, but we've already set it above.
        self.merge(path=self.path, settings=settings, override=True, set_path=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the settings store."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any, save: bool = False) -> None:
        """Update a single value. If save=True, writes the entire store to disk."""
        self._data[key] = value
        if save:
            self.save()

    def as_dict(self) -> dict[str, Any]:
        """Return a copy of the internal settings dictionary."""
        return dict(self._data)

    def load(
        self, 
        path: Path | str | None = None, 
        settings: dict[str, Any] | SettingsProtocol | None = None, 
        override: bool = False,
        set_path: bool = False
    ) -> None:
        """Replace current memory with new data from disk and/or source."""
        self._data.clear()
        # Loading into empty memory means override=True effectively.
        self.merge(path=path, settings=settings, override=True, set_path=set_path)

    def merge(
        self, 
        path: Path | str | None = None, 
        settings: dict[str, Any] | SettingsProtocol | None = None, 
        override: bool = False,
        set_path: bool = False
    ) -> None:
        """
        Combine external data with the current settings.
        
        Parameters:
            path: Optional disk path to load from.
            settings: Dictionary or Settings object to merge.
            override: If True, incoming keys replace existing keys.
            set_path: If True, updates the instance's default path to 'path'.
        """
        incoming: dict[str, Any] = {}
        target_path = Path(path).expanduser().resolve() if path else self.path

        # 1. Update internal path if requested
        if path and set_path:
            self.path = target_path

        # 2. Read from file if valid
        if target_path and target_path.exists():
            try:
                with target_path.open("r", encoding="utf-8") as f:
                    incoming.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass

        # 3. Merge polymorphic source
        if settings is not None:
            if hasattr(settings, "as_dict") and callable(settings.as_dict):
                incoming.update(settings.as_dict())
            elif isinstance(settings, dict):
                incoming.update(settings)

        # 4. Apply into memory based on override flag
        if override:
            self._data.update(incoming)
        else:
            for k, v in incoming.items():
                if k not in self._data:
                    self._data[k] = v

    def save(
        self, 
        path: Path | str | None = None, 
        settings: dict[str, Any] | SettingsProtocol | None = None,
        set_path: bool = False
    ) -> None:
        """Persist settings to disk."""
        target_path = Path(path).expanduser().resolve() if path else self.path

        if path and set_path:
            self.path = target_path

        # Merge data if provided before saving (overriding memory)
        if settings is not None:
            self.merge(settings=settings, override=True)

        if not target_path:
            return

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = target_path.with_suffix(".tmp")
            with temp_path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
            os.replace(temp_path, target_path)
        except OSError:
            pass

    def clear(self, save: bool = False) -> None:
        """Wipe all settings from memory."""
        self._data.clear()
        if save:
            self.save()

    def __repr__(self) -> str:
        return f"Settings(path={self.path}, keys={list(self._data.keys())})"
