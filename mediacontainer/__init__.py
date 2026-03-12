"""
# MediaContainer — Library Initialization

## Calling API
- `from mediacontainer import ClassifiedFile, FileType, MediaContainer`:
  Primary exports for consuming the MediaContainer library.

## Algorithmic Methodology
- Exposes core classes and enums to simplify the import interface.

## Program Flow
1. Imports key symbols from `media_container.py`.
2. Defines `__all__` for clean namespace management.
"""

from .media_container import ClassifiedFile, FileType, MediaContainer

__all__ = ["ClassifiedFile", "FileType", "MediaContainer"]
