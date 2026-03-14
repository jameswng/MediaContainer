"""
# SyslogLogger — Standalone Native System Logging

## Calling API
- `log_error(ident: str, message: str)`
- `log_warning(ident: str, message: str)`
- `log_info(ident: str, message: str)`

## Algorithmic Methodology
- Provides a zero-dependency interface to the Unix/macOS syslog daemon.
"""

import syslog

def _log(ident: str, message: str, priority: int) -> None:
    syslog.openlog(ident=ident, facility=syslog.LOG_USER)
    syslog.syslog(priority, message)
    syslog.closelog()

def log_error(ident: str, message: str) -> None:
    _log(ident, f"[ERROR] {message}", syslog.LOG_ERR)

def log_warning(ident: str, message: str) -> None:
    _log(ident, f"[WARNING] {message}", syslog.LOG_WARNING)

def log_info(ident: str, message: str) -> None:
    _log(ident, f"[INFO] {message}", syslog.LOG_INFO)
