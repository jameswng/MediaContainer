"""
# SyslogLogger — Library Initialization
"""
from .logger import log_error, log_warning, log_info
from .protocol import LoggingProtocol

__all__ = ["log_error", "log_warning", "log_info", "LoggingProtocol"]
