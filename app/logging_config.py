"""Logging configuration for Voice Text Processor.

This module sets up the logging system with proper formatting, levels,
and file output. It also includes a filter to prevent sensitive information
from being logged.

Requirements: 10.5, 9.5
"""

import logging
import re
from typing import Optional
from pathlib import Path
from contextvars import ContextVar


# Context variable to store request_id across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class RequestIdFilter(logging.Filter):
    """Filter to add request_id to log records.
    
    This filter adds the request_id from context to each log record,
    making it available in the log format.
    
    Requirements: 9.5
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to log record.
        
        Args:
            record: Log record to enhance
            
        Returns:
            bool: Always True (we modify but don't reject records)
        """
        # Get request_id from context, default to empty string if not set
        record.request_id = request_id_var.get() or '-'
        return True


class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive information from log records.
    
    This filter masks API keys, passwords, and other sensitive data
    to prevent them from appearing in logs.
    
    Requirements: 10.5
    """
    
    # Patterns to detect and mask sensitive data
    SENSITIVE_PATTERNS = [
        # API keys (various formats)
        (re.compile(r'(api[_-]?key["\s:=]+)([a-zA-Z0-9_-]{10,})', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(zhipu[_-]?api[_-]?key["\s:=]+)([a-zA-Z0-9_-]{10,})', re.IGNORECASE), r'\1***REDACTED***'),
        # Bearer tokens
        (re.compile(r'(bearer\s+)([a-zA-Z0-9_-]{10,})', re.IGNORECASE), r'\1***REDACTED***'),
        # Passwords
        (re.compile(r'(password["\s:=]+)([^\s"]+)', re.IGNORECASE), r'\1***REDACTED***'),
        # Authorization headers (capture the whole value)
        (re.compile(r'(authorization["\s:=]+)([^\s"]+)', re.IGNORECASE), r'\1***REDACTED***'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to mask sensitive data.
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: Always True (we modify but don't reject records)
        """
        # Mask sensitive data in the message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._mask_sensitive_data(record.msg)
        
        # Mask sensitive data in arguments
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._mask_sensitive_data(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._mask_sensitive_data(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        
        return True
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text using regex patterns.
        
        Args:
            text: Text to mask
            
        Returns:
            str: Text with sensitive data masked
        """
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    log_format: Optional[str] = None
) -> None:
    """Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs only to console.
        log_format: Optional custom log format string
        
    Requirements: 10.5, 9.5
    """
    # Default log format with request_id, timestamp, level, and message
    if log_format is None:
        log_format = "[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
    
    # Date format
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add filters
    request_id_filter = RequestIdFilter()
    sensitive_filter = SensitiveDataFilter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_id_filter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(request_id_filter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at level {log_level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """Set the request_id in the current context.
    
    This should be called at the beginning of each request to ensure
    all log messages include the request_id.
    
    Args:
        request_id: Unique identifier for the request
        
    Requirements: 9.5
    """
    request_id_var.set(request_id)


def clear_request_id() -> None:
    """Clear the request_id from the current context.
    
    This should be called at the end of each request to clean up.
    """
    request_id_var.set(None)
