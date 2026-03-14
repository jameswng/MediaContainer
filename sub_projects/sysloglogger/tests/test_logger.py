"""
# SyslogLogger — Unit Tests
"""

from unittest.mock import patch
import syslog
from sub_projects.sysloglogger import logger as sysloglogger

def test_log_error():
    with patch("syslog.syslog") as mock_syslog, \
         patch("syslog.openlog") as mock_openlog, \
         patch("syslog.closelog") as mock_closelog:
        
        sysloglogger.log_error("test_ident", "test_message")
        
        mock_openlog.assert_called_once_with(ident="test_ident", facility=syslog.LOG_USER)
        mock_syslog.assert_called_once_with(syslog.LOG_ERR, "[ERROR] test_message")
        mock_closelog.assert_called_once()

def test_log_warning():
    with patch("syslog.syslog") as mock_syslog, \
         patch("syslog.openlog") as mock_openlog, \
         patch("syslog.closelog") as mock_closelog:
        
        sysloglogger.log_warning("test_ident", "test_message")
        
        mock_openlog.assert_called_once_with(ident="test_ident", facility=syslog.LOG_USER)
        mock_syslog.assert_called_once_with(syslog.LOG_WARNING, "[WARNING] test_message")
        mock_closelog.assert_called_once()

def test_log_info():
    with patch("syslog.syslog") as mock_syslog, \
         patch("syslog.openlog") as mock_openlog, \
         patch("syslog.closelog") as mock_closelog:
        
        sysloglogger.log_info("test_ident", "test_message")
        
        mock_openlog.assert_called_once_with(ident="test_ident", facility=syslog.LOG_USER)
        mock_syslog.assert_called_once_with(syslog.LOG_INFO, "[INFO] test_message")
        mock_closelog.assert_called_once()
