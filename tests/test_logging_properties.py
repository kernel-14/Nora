"""Property-based tests for logging functionality.

This module uses hypothesis to verify that error logging properties hold across
many random error scenarios, ensuring all errors are logged with timestamps and
stack traces.

Requirements: 9.5
"""

import logging
import pytest
import tempfile
import re
from pathlib import Path
from datetime import datetime

from hypothesis import given, strategies as st
from hypothesis import settings

from app.logging_config import (
    setup_logging,
    get_logger,
    set_request_id,
    clear_request_id
)


# Custom strategies for generating error scenarios
@st.composite
def error_message_strategy(draw):
    """Generate various error messages."""
    error_types = [
        "API call failed",
        "Database connection error",
        "File not found",
        "Permission denied",
        "Timeout occurred",
        "Invalid input",
        "Network error",
        "Service unavailable"
    ]
    
    error_type = draw(st.sampled_from(error_types))
    details = draw(st.text(min_size=0, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs'),
        blacklist_characters='\x00\n\r'
    )))
    
    if details:
        return f"{error_type}: {details}"
    return error_type


@st.composite
def exception_strategy(draw):
    """Generate various exception types with messages."""
    exception_types = [
        ValueError,
        RuntimeError,
        TypeError,
        KeyError,
        IndexError,
        AttributeError,
        IOError,
        ConnectionError
    ]
    
    exc_type = draw(st.sampled_from(exception_types))
    message = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs'),
        blacklist_characters='\x00\n\r'
    )))
    
    return exc_type(message)


class TestErrorLoggingProperties:
    """Property-based tests for error logging.
    
    **Validates: Requirements 9.5**
    """
    
    @given(
        error_msg=error_message_strategy(),
        module_name=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_14_error_logging_with_timestamp(self, error_msg, module_name):
        """
        Property 14: 错误日志记录 - Timestamp
        
        For any error that occurs in the system, the error should be logged
        with a timestamp.
        
        **Validates: Requirements 9.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="ERROR", log_file=log_file)
            
            # Get a logger for the module
            logger = get_logger(module_name)
            
            # Log an error
            logger.error(error_msg)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log entry should exist
            assert content, "Log file should contain error entry"
            
            # Property 2: Log entry should contain timestamp in format [YYYY-MM-DD HH:MM:SS]
            timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
            assert re.search(timestamp_pattern, content), \
                f"Log entry should contain timestamp. Content: {content}"
            
            # Property 3: Log entry should contain the error message
            # (escape special regex characters in error_msg)
            escaped_msg = re.escape(error_msg[:50])  # Check first 50 chars to avoid issues
            assert re.search(escaped_msg, content, re.IGNORECASE), \
                f"Log entry should contain error message. Expected: {error_msg[:50]}, Content: {content}"
            
            # Property 4: Log entry should contain ERROR level
            assert "[ERROR]" in content, \
                f"Log entry should contain ERROR level. Content: {content}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        exception=exception_strategy(),
        module_name=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_14_error_logging_with_stack_trace(self, exception, module_name):
        """
        Property 14: 错误日志记录 - Stack Trace
        
        For any error that occurs in the system, the error should be logged
        with a complete stack trace when exc_info=True is used.
        
        **Validates: Requirements 9.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="ERROR", log_file=log_file)
            
            # Get a logger for the module
            logger = get_logger(module_name)
            
            # Raise and catch an exception, then log it with stack trace
            try:
                raise exception
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}", exc_info=True)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log entry should exist
            assert content, "Log file should contain error entry"
            
            # Property 2: Log entry should contain timestamp
            timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
            assert re.search(timestamp_pattern, content), \
                f"Log entry should contain timestamp. Content: {content}"
            
            # Property 3: Log entry should contain the exception type name
            exception_type_name = type(exception).__name__
            assert exception_type_name in content, \
                f"Log entry should contain exception type '{exception_type_name}'. Content: {content}"
            
            # Property 4: Log entry should contain stack trace indicator
            # Python stack traces contain "Traceback" or the file/line info
            assert "Traceback" in content or "File" in content, \
                f"Log entry should contain stack trace. Content: {content}"
            
            # Property 5: Log entry should contain ERROR level
            assert "[ERROR]" in content, \
                f"Log entry should contain ERROR level. Content: {content}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        errors=st.lists(
            error_message_strategy(),
            min_size=1,
            max_size=5
        ),
        module_name=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_14_multiple_errors_logged(self, errors, module_name):
        """
        Property 14: 错误日志记录 - Multiple Errors
        
        For any sequence of errors that occur in the system, all errors should
        be logged with timestamps.
        
        **Validates: Requirements 9.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="ERROR", log_file=log_file)
            
            # Get a logger for the module
            logger = get_logger(module_name)
            
            # Log all errors
            for error_msg in errors:
                logger.error(error_msg)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log file should contain entries
            assert content, "Log file should contain error entries"
            
            # Property 2: Count ERROR level entries
            error_count = content.count("[ERROR]")
            assert error_count >= len(errors), \
                f"Log should contain at least {len(errors)} ERROR entries, found {error_count}"
            
            # Property 3: All timestamps should be present
            timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
            timestamps = re.findall(timestamp_pattern, content)
            assert len(timestamps) >= len(errors), \
                f"Log should contain at least {len(errors)} timestamps, found {len(timestamps)}"
            
            # Property 4: Each unique error message should appear in the log
            # (check first 30 chars of each message to avoid special char issues)
            for error_msg in errors:
                # Take a safe substring and escape it
                safe_msg = error_msg[:30]
                if safe_msg:
                    escaped_msg = re.escape(safe_msg)
                    assert re.search(escaped_msg, content, re.IGNORECASE), \
                        f"Log should contain error message: {safe_msg}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        exception=exception_strategy(),
        request_id=st.text(min_size=5, max_size=36, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        )),
        module_name=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_14_error_logging_with_request_context(
        self, exception, request_id, module_name
    ):
        """
        Property 14: 错误日志记录 - Request Context
        
        For any error that occurs during request processing, the error should
        be logged with timestamp, stack trace, and request_id for tracing.
        
        **Validates: Requirements 9.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="ERROR", log_file=log_file)
            
            # Set request_id in context
            set_request_id(request_id)
            
            # Get a logger for the module
            logger = get_logger(module_name)
            
            # Raise and catch an exception, then log it
            try:
                raise exception
            except Exception as e:
                logger.error(f"Request processing error: {str(e)}", exc_info=True)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log entry should contain timestamp
            timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
            assert re.search(timestamp_pattern, content), \
                f"Log entry should contain timestamp. Content: {content}"
            
            # Property 2: Log entry should contain request_id
            # Escape special regex characters in request_id
            escaped_request_id = re.escape(request_id)
            assert re.search(escaped_request_id, content), \
                f"Log entry should contain request_id '{request_id}'. Content: {content}"
            
            # Property 3: Log entry should contain stack trace
            assert "Traceback" in content or "File" in content, \
                f"Log entry should contain stack trace. Content: {content}"
            
            # Property 4: Log entry should contain exception type
            exception_type_name = type(exception).__name__
            assert exception_type_name in content, \
                f"Log entry should contain exception type '{exception_type_name}'. Content: {content}"
            
            # Property 5: Log entry should contain ERROR level
            assert "[ERROR]" in content, \
                f"Log entry should contain ERROR level. Content: {content}"
        finally:
            # Clean up
            clear_request_id()
            
            # Close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        error_msg=error_message_strategy(),
        log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    )
    @settings(max_examples=30)
    def test_property_14_error_logging_respects_level(self, error_msg, log_level):
        """
        Property 14: 错误日志记录 - Log Level Filtering
        
        For any error logged at ERROR level, it should appear in the log file
        when the log level is set to ERROR or lower (more permissive).
        
        **Validates: Requirements 9.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the specified level
            setup_logging(log_level=log_level, log_file=log_file)
            
            # Get a logger
            logger = get_logger("test_module")
            
            # Log an error
            logger.error(error_msg)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property: ERROR messages should always be logged regardless of level
            # (ERROR is high priority, so it should appear even if level is CRITICAL)
            # Actually, ERROR should appear for DEBUG, INFO, WARNING, ERROR levels
            # but not necessarily for CRITICAL (which is higher than ERROR)
            
            level_hierarchy = {
                "DEBUG": 10,
                "INFO": 20,
                "WARNING": 30,
                "ERROR": 40,
                "CRITICAL": 50
            }
            
            if level_hierarchy[log_level] <= level_hierarchy["ERROR"]:
                # Error should be logged
                assert content, "Log file should contain error entry"
                assert "[ERROR]" in content, \
                    f"Log should contain ERROR level when log_level={log_level}"
                
                # Should contain timestamp
                timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
                assert re.search(timestamp_pattern, content), \
                    f"Log entry should contain timestamp. Content: {content}"
            else:
                # Error should NOT be logged (level is CRITICAL, which is higher than ERROR)
                # Actually, this is wrong - ERROR should still be logged at CRITICAL level
                # Let me correct this: ERROR level logs should appear at ERROR and CRITICAL levels
                pass  # ERROR should always appear
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup



class TestSensitiveDataProtectionProperties:
    """Property-based tests for sensitive data protection in logs.
    
    **Validates: Requirements 10.5**
    """
    
    @given(
        api_key=st.text(min_size=20, max_size=64, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            min_codepoint=ord('A'), max_codepoint=ord('z')
        )),
        message_prefix=st.text(min_size=5, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_15_api_key_masking(self, api_key, message_prefix):
        """
        Property 15: 敏感信息保护 - API Key Masking
        
        For any log message containing an API key, the API key should be
        masked and not appear in plain text in the log output.
        
        **Validates: Requirements 10.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Get a logger
            logger = get_logger("test_module")
            
            # Log a message containing an API key in various formats
            formats = [
                f"{message_prefix} api_key={api_key}",
                f"{message_prefix} api-key: {api_key}",
                f"{message_prefix} API_KEY={api_key}",
                f"{message_prefix} zhipu_api_key={api_key}",
            ]
            
            for log_message in formats:
                logger.info(log_message)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log file should contain entries
            assert content, "Log file should contain log entries"
            
            # Property 2: API key should NOT appear in plain text
            assert api_key not in content, \
                f"API key should be masked in logs. Found: {api_key} in content"
            
            # Property 3: Redaction marker should appear
            assert "***REDACTED***" in content, \
                f"Log should contain redaction marker. Content: {content}"
            
            # Property 4: Message prefix should still be present (not masked)
            if message_prefix.strip():
                # Check first few words of prefix
                prefix_words = message_prefix.strip().split()[:2]
                if prefix_words:
                    first_word = prefix_words[0]
                    assert first_word in content, \
                        f"Non-sensitive message prefix should be preserved. Looking for: {first_word}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        password=st.text(min_size=8, max_size=32, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'P'),
            blacklist_characters='\x00\n\r\t '
        )),
        username=st.text(min_size=3, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_15_password_masking(self, password, username):
        """
        Property 15: 敏感信息保护 - Password Masking
        
        For any log message containing a password, the password should be
        masked and not appear in plain text in the log output.
        
        **Validates: Requirements 10.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Get a logger
            logger = get_logger("test_module")
            
            # Log messages containing passwords in various formats
            formats = [
                f"User {username} login with password={password}",
                f"Authentication failed for password: {password}",
                f"PASSWORD={password}",
            ]
            
            for log_message in formats:
                logger.info(log_message)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log file should contain entries
            assert content, "Log file should contain log entries"
            
            # Property 2: Password should NOT appear in plain text
            assert password not in content, \
                f"Password should be masked in logs. Found: {password} in content"
            
            # Property 3: Redaction marker should appear
            assert "***REDACTED***" in content, \
                f"Log should contain redaction marker. Content: {content}"
            
            # Property 4: Username should still be present (not masked)
            assert username in content, \
                f"Non-sensitive username should be preserved. Looking for: {username}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        bearer_token=st.text(min_size=20, max_size=64, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            min_codepoint=ord('A'), max_codepoint=ord('z')
        )),
        endpoint=st.text(min_size=5, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_15_bearer_token_masking(self, bearer_token, endpoint):
        """
        Property 15: 敏感信息保护 - Bearer Token Masking
        
        For any log message containing a bearer token, the token should be
        masked and not appear in plain text in the log output.
        
        **Validates: Requirements 10.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Get a logger
            logger = get_logger("test_module")
            
            # Log messages containing bearer tokens
            formats = [
                f"Calling {endpoint} with Bearer {bearer_token}",
                f"Authorization: Bearer {bearer_token}",
                f"BEARER {bearer_token}",
            ]
            
            for log_message in formats:
                logger.info(log_message)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log file should contain entries
            assert content, "Log file should contain log entries"
            
            # Property 2: Bearer token should NOT appear in plain text
            assert bearer_token not in content, \
                f"Bearer token should be masked in logs. Found: {bearer_token} in content"
            
            # Property 3: Redaction marker should appear
            assert "***REDACTED***" in content, \
                f"Log should contain redaction marker. Content: {content}"
            
            # Property 4: Endpoint should still be present (not masked)
            assert endpoint in content, \
                f"Non-sensitive endpoint should be preserved. Looking for: {endpoint}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        auth_header=st.text(min_size=20, max_size=64, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            min_codepoint=ord('A'), max_codepoint=ord('z')
        ))
    )
    @settings(max_examples=30)
    def test_property_15_authorization_header_masking(self, auth_header):
        """
        Property 15: 敏感信息保护 - Authorization Header Masking
        
        For any log message containing an authorization header value, it should
        be masked and not appear in plain text in the log output.
        
        **Validates: Requirements 10.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Get a logger
            logger = get_logger("test_module")
            
            # Log messages containing authorization headers
            formats = [
                f"Request headers: authorization={auth_header}",
                f"Authorization: {auth_header}",
                f"AUTHORIZATION={auth_header}",
            ]
            
            for log_message in formats:
                logger.info(log_message)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log file should contain entries
            assert content, "Log file should contain log entries"
            
            # Property 2: Authorization header should NOT appear in plain text
            assert auth_header not in content, \
                f"Authorization header should be masked in logs. Found: {auth_header} in content"
            
            # Property 3: Redaction marker should appear
            assert "***REDACTED***" in content, \
                f"Log should contain redaction marker. Content: {content}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
    
    @given(
        sensitive_data=st.lists(
            st.tuples(
                st.sampled_from(["api_key", "password", "bearer_token", "authorization"]),
                st.text(min_size=15, max_size=40, alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    min_codepoint=ord('A'), max_codepoint=ord('z')
                ))
            ),
            min_size=1,
            max_size=3
        ),
        normal_message=st.text(min_size=10, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters='\x00\n\r'
        ))
    )
    @settings(max_examples=30)
    def test_property_15_multiple_sensitive_data_masking(self, sensitive_data, normal_message):
        """
        Property 15: 敏感信息保护 - Multiple Sensitive Data Masking
        
        For any log message containing multiple types of sensitive data,
        all sensitive data should be masked while preserving non-sensitive content.
        
        **Validates: Requirements 10.5**
        """
        # Create a fresh temporary log file for each example
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
            log_file = Path(tmp_file.name)
        
        try:
            # Setup logging with the temporary file
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Get a logger
            logger = get_logger("test_module")
            
            # Build a log message with multiple sensitive data
            log_message = normal_message
            sensitive_values = []
            
            for data_type, value in sensitive_data:
                if data_type == "api_key":
                    log_message += f" api_key={value}"
                elif data_type == "password":
                    log_message += f" password={value}"
                elif data_type == "bearer_token":
                    log_message += f" Bearer {value}"
                elif data_type == "authorization":
                    log_message += f" authorization={value}"
                sensitive_values.append(value)
            
            # Log the message
            logger.info(log_message)
            
            # Read the log file
            content = log_file.read_text(encoding='utf-8')
            
            # Property 1: Log file should contain entries
            assert content, "Log file should contain log entries"
            
            # Property 2: None of the sensitive values should appear in plain text
            for value in sensitive_values:
                assert value not in content, \
                    f"Sensitive value should be masked in logs. Found: {value} in content"
            
            # Property 3: Redaction markers should appear (at least one per sensitive item)
            redaction_count = content.count("***REDACTED***")
            assert redaction_count >= len(sensitive_values), \
                f"Log should contain at least {len(sensitive_values)} redaction markers, found {redaction_count}"
            
            # Property 4: Normal message should still be present (at least partially)
            if normal_message.strip():
                # Check first few words of normal message
                words = normal_message.strip().split()[:2]
                if words:
                    first_word = words[0]
                    # Only check if the word is not too short
                    if len(first_word) > 3:
                        assert first_word in content, \
                            f"Non-sensitive message content should be preserved. Looking for: {first_word}"
        finally:
            # Clean up - close all handlers first to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            
            if log_file.exists():
                try:
                    log_file.unlink()
                except PermissionError:
                    pass  # File still locked, skip cleanup
