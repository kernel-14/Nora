"""Tests for logging configuration module.

Requirements: 10.5, 9.5
"""

import logging
import pytest
from pathlib import Path

from app.logging_config import (
    SensitiveDataFilter,
    RequestIdFilter,
    setup_logging,
    get_logger,
    set_request_id,
    clear_request_id
)


class TestRequestIdFilter:
    """Test request_id filtering in logs.
    
    Requirement 9.5: Logs should include request_id for tracing.
    """
    
    def test_filter_adds_request_id(self):
        """Test that request_id is added to log records."""
        filter_obj = RequestIdFilter()
        
        # Set request_id in context
        set_request_id("test-request-123")
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert hasattr(record, 'request_id')
        assert record.request_id == "test-request-123"
        
        # Clean up
        clear_request_id()
    
    def test_filter_uses_default_when_no_request_id(self):
        """Test that filter uses '-' when no request_id is set."""
        filter_obj = RequestIdFilter()
        
        # Ensure no request_id is set
        clear_request_id()
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert hasattr(record, 'request_id')
        assert record.request_id == "-"


class TestSensitiveDataFilter:
    """Test sensitive data filtering in logs.
    
    Requirement 10.5: System should not output sensitive information in logs.
    """
    
    def test_filter_api_key(self):
        """Test that API keys are masked in log messages."""
        filter_obj = SensitiveDataFilter()
        
        # Create a log record with API key
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Using api_key=sk_1234567890abcdef for request",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "sk_1234567890abcdef" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_filter_zhipu_api_key(self):
        """Test that Zhipu API keys are masked."""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="zhipu_api_key: abc123def456ghi789",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "abc123def456ghi789" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_filter_bearer_token(self):
        """Test that bearer tokens are masked."""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_filter_password(self):
        """Test that passwords are masked."""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='Login attempt with password="secret123"',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "secret123" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_filter_authorization_header(self):
        """Test that authorization headers are masked."""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Headers: authorization: Basic_dXNlcjpwYXNz",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "Basic_dXNlcjpwYXNz" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_filter_preserves_normal_text(self):
        """Test that normal text is not affected by filtering."""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processing request for user authentication",
            args=(),
            exc_info=None
        )
        
        original_msg = record.msg
        filter_obj.filter(record)
        
        assert record.msg == original_msg
    
    def test_filter_with_args_dict(self):
        """Test filtering with dictionary arguments."""
        filter_obj = SensitiveDataFilter()
        
        # Create record with dict args
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request data",
            args=(),
            exc_info=None
        )
        # Manually set args after creation
        record.args = {"data": "api_key=secret123456"}
        
        filter_obj.filter(record)
        
        assert "secret123456" not in record.args["data"]
        assert "***REDACTED***" in record.args["data"]
    
    def test_filter_with_args_tuple(self):
        """Test filtering with tuple arguments."""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Config: %s",
            args=("api_key=secret123456",),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "secret123456" not in record.args[0]
        assert "***REDACTED***" in record.args[0]


class TestSetupLogging:
    """Test logging setup and configuration."""
    
    def test_setup_logging_console_only(self):
        """Test setting up logging with console output only."""
        setup_logging(log_level="INFO", log_file=None)
        
        root_logger = logging.getLogger()
        
        # Should have at least one handler (console)
        assert len(root_logger.handlers) >= 1
        
        # Check log level
        assert root_logger.level == logging.INFO
    
    def test_setup_logging_with_file(self, tmp_path):
        """Test setting up logging with file output."""
        log_file = tmp_path / "test.log"
        
        setup_logging(log_level="DEBUG", log_file=log_file)
        
        root_logger = logging.getLogger()
        
        # Should have at least two handlers (console + file)
        assert len(root_logger.handlers) >= 2
        
        # Check log level
        assert root_logger.level == logging.DEBUG
        
        # Test logging to file
        test_logger = logging.getLogger("test")
        test_logger.info("Test message")
        
        # File should exist and contain the message
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content
    
    def test_setup_logging_custom_format(self, tmp_path):
        """Test setting up logging with custom format."""
        log_file = tmp_path / "test.log"
        custom_format = "%(levelname)s - %(message)s"
        
        setup_logging(
            log_level="INFO",
            log_file=log_file,
            log_format=custom_format
        )
        
        test_logger = logging.getLogger("test_custom")
        test_logger.info("Custom format test")
        
        content = log_file.read_text()
        assert "INFO - Custom format test" in content
    
    def test_setup_logging_applies_sensitive_filter(self, tmp_path):
        """Test that sensitive data filter is applied to all handlers.
        
        Requirement 10.5: Sensitive information should be filtered from logs.
        """
        log_file = tmp_path / "test.log"
        
        setup_logging(log_level="INFO", log_file=log_file)
        
        test_logger = logging.getLogger("test_sensitive")
        test_logger.info("API request with api_key=secret123456789")
        
        # Read log file
        content = log_file.read_text()
        
        # API key should be redacted
        assert "secret123456789" not in content
        assert "***REDACTED***" in content
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")
        
        assert logger is not None
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)


class TestLoggingIntegration:
    """Integration tests for logging system.
    
    Requirement 9.5: System should log all errors with timestamp and stack trace.
    """
    
    def test_error_logging_with_traceback(self, tmp_path):
        """Test that errors are logged with full traceback."""
        log_file = tmp_path / "error.log"
        
        setup_logging(log_level="ERROR", log_file=log_file)
        
        logger = get_logger("test_error")
        
        try:
            # Cause an error
            raise ValueError("Test error for logging")
        except ValueError:
            logger.error("An error occurred", exc_info=True)
        
        # Read log file
        content = log_file.read_text()
        
        # Should contain error message and traceback
        assert "An error occurred" in content
        assert "ValueError: Test error for logging" in content
        assert "Traceback" in content
    
    def test_logging_includes_timestamp(self, tmp_path):
        """Test that log entries include timestamps."""
        log_file = tmp_path / "timestamp.log"
        
        setup_logging(log_level="INFO", log_file=log_file)
        
        logger = get_logger("test_timestamp")
        logger.info("Timestamp test message")
        
        content = log_file.read_text()
        
        # Should contain timestamp in format [YYYY-MM-DD HH:MM:SS]
        import re
        timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
        assert re.search(timestamp_pattern, content)
    
    def test_logging_includes_level_and_module(self, tmp_path):
        """Test that log entries include level and module name."""
        log_file = tmp_path / "format.log"
        
        setup_logging(log_level="INFO", log_file=log_file)
        
        logger = get_logger("test_module")
        logger.warning("Warning message")
        
        content = log_file.read_text()
        
        # Should contain level and module name
        assert "[WARNING]" in content
        assert "[test_module]" in content
        assert "Warning message" in content
    
    def test_logging_includes_request_id(self, tmp_path):
        """Test that log entries include request_id when set.
        
        Requirement 9.5: Logs should include request_id for request tracing.
        """
        log_file = tmp_path / "request_id.log"
        
        setup_logging(log_level="INFO", log_file=log_file)
        
        # Set request_id
        set_request_id("req-12345")
        
        logger = get_logger("test_request")
        logger.info("Request message")
        
        content = log_file.read_text()
        
        # Should contain request_id
        assert "[req-12345]" in content
        assert "Request message" in content
        
        # Clean up
        clear_request_id()
    
    def test_logging_without_request_id(self, tmp_path):
        """Test that log entries use '-' when no request_id is set."""
        log_file = tmp_path / "no_request_id.log"
        
        setup_logging(log_level="INFO", log_file=log_file)
        
        # Ensure no request_id is set
        clear_request_id()
        
        logger = get_logger("test_no_request")
        logger.info("Message without request_id")
        
        content = log_file.read_text()
        
        # Should contain '-' for request_id
        assert "[-]" in content
        assert "Message without request_id" in content
