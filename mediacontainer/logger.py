"""
# MediaContainer — Native System Logging Utility

## Calling API
- `log_error(message: str)`: Reports a critical error to the system logger.
- `log_warning(message: str)`: Reports a warning to the system logger.
- `log_info(message: str)`: Reports informational status out-of-band.

## Algorithmic Methodology
- **syslog**: Uses the standard Unix/macOS syslog interface for out-of-band logging.
- **Decoupled Reporting**: Ensures critical failures are recorded even if stdout/stderr are redirected.

## Program Flow
1. Open a connection to the system log daemon with the 'mediacontainer' identity.
2. Provide simple functions to dispatch messages at appropriate priority levels.
"""

import syslog

def _log(message: str, priority: int) -> None:
    """Internal dispatcher for syslog."""
    syslog.openlog(ident="mediacontainer", facility=syslog.LOG_USER)
    syslog.syslog(priority, message)
    syslog.closelog()

def log_error(message: str) -> None:
    """Log a critical error to the system log."""
    _log(f"[ERROR] {message}", syslog.LOG_ERR)

def log_warning(message: str) -> None:
    """Log a warning to the system log."""
    _log(f"[WARNING] {message}", syslog.LOG_WARNING)

def log_info(message: str) -> None:
    """Log informational status to the system log."""
    _log(f"[INFO] {message}", syslog.LOG_INFO)
