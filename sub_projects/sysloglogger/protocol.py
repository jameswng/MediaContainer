"""
# SyslogLogger — Formal Logging Protocol

## Calling API
- `LoggingProtocol`: Protocol defining the interface for system logging.
- `log_error(ident: str, message: str)`: Interface method for logging errors.
- `log_warning(ident: str, message: str)`: Interface method for logging warnings.
- `log_info(ident: str, message: str)`: Interface method for logging info.

## Algorithmic Methodology
- Uses `typing.Protocol` and `typing.runtime_checkable` for structural typing.
- Provides a unified interface that multiple loggers can implement.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LoggingProtocol(Protocol):
    """Protocol defining the expected interface for system logging."""

    def log_error(self, ident: str, message: str) -> None:
        """Report a critical error to the system logger."""
        ...

    def log_warning(self, ident: str, message: str) -> None:
        """Report a warning to the system logger."""
        ...

    def log_info(self, ident: str, message: str) -> None:
        """Report informational status out-of-band."""
        ...
