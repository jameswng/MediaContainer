"""
# ManagedSettings — Persistent Key-Value Configuration

## Calling API
- `from managedsettings import Settings`: Primary class for managing settings.
- `Settings(path: Path | str | None = None)`: Initialize with optional persistence.

## Algorithmic Methodology
- Implements a dictionary-backed store with JSON serialization.
- Provides a "load-on-init, save-on-demand" workflow.

## Program Flow
1. Exposes the `Settings` class for external consumption.
"""

from .settings import Settings

__all__ = ["Settings"]
