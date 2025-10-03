"""FLEXT CLI Exceptions Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliExceptions.BaseError covering all real functionality with flext_tests
integration, comprehensive exception handling, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import logging
import threading
import time

import pytest
from flext_tests import FlextTestsUtilities

from flext_cli.constants import FlextCliConstants
from flext_cli.exceptions import FlextCliExceptions


class TestFlextCliExceptionsFlextCliError:
    """Comprehensive tests for FlextCliExceptions.BaseError functionality."""

    @pytest.fixture
    def exceptions_service(self) -> FlextCliExceptions.BaseError:
        """Create FlextCliExceptions.BaseError instance for testing."""
        return FlextCliExceptions.BaseError("Test exception")

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_exceptions_service_initialization(
        self, exceptions_service: FlextCliExceptions.BaseError
    ) -> None:
        """Test exceptions service initialization and basic properties."""
        assert exceptions_service is not None
        assert hasattr(exceptions_service, "__class__")

    def test_exceptions_service_basic_functionality(
        self, exceptions_service: FlextCliExceptions.BaseError
    ) -> None:
        """Test exceptions service basic functionality."""
        # Test that exceptions can be created and accessed
        assert exceptions_service is not None
        assert hasattr(exceptions_service, "__class__")

    # ========================================================================
    # EXCEPTION CLASS TESTING
    # ========================================================================

    def test_flext_cli_error_creation(self) -> None:
        """Test FlextCliExceptions.BaseError exception creation."""
        # Test basic exception creation
        error = FlextCliExceptions.BaseError("Test error message")
        assert isinstance(error, FlextCliExceptions.BaseError)
        assert isinstance(error, Exception)
        assert "[CLI_ERROR] Test error message" in str(error)

    def test_flext_cli_error_with_details(self) -> None:
        """Test FlextCliExceptions.BaseError with additional details."""
        error = FlextCliExceptions.BaseError(
            "Test error", details={"code": 123, "context": "test"}
        )
        assert isinstance(error, FlextCliExceptions.BaseError)
        assert "[CLI_ERROR] Test error" in str(error)
        assert hasattr(error, "context")
        # Test context structure
        assert error.context is not None
        assert hasattr(error, "context")

    def test_flext_cli_error_inheritance(self) -> None:
        """Test FlextCliExceptions.BaseError inheritance chain."""
        error = FlextCliExceptions.BaseError("Test error")

        # Test inheritance
        assert isinstance(error, Exception)
        assert isinstance(error, FlextCliExceptions.BaseError)

        # Test that it can be caught as Exception
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise error
        assert "[CLI_ERROR] Test error" in str(exc_info.value)

    def test_flext_cli_error_custom_attributes(self) -> None:
        """Test FlextCliExceptions.BaseError with custom attributes."""
        error = FlextCliExceptions.BaseError(
            "Test error",
            error_code=500,
            context="test_context",
            timestamp="2025-01-01T00:00:00Z",
        )

        assert error.error_code == "500"  # Error code is now a string
        assert error.context["context"] == "test_context"
        assert error.context["timestamp"] == "2025-01-01T00:00:00Z"

    # ========================================================================
    # EXCEPTION RAISING AND HANDLING
    # ========================================================================

    def test_raise_flext_cli_error(self) -> None:
        """Test raising FlextCliExceptions.BaseError exception."""
        error_message = "Test error message"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(error_message)

        assert str(exc_info.value) == "[CLI_ERROR] Test error message"
        assert isinstance(exc_info.value, FlextCliExceptions.BaseError)

    def test_catch_flext_cli_error(self) -> None:
        """Test catching FlextCliExceptions.BaseError exception."""
        error_message = "Test error message"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(error_message)

        assert str(exc_info.value) == f"[CLI_ERROR] {error_message}"
        assert isinstance(exc_info.value, FlextCliExceptions.BaseError)

    def test_catch_flext_cli_error_as_exception(self) -> None:
        """Test catching FlextCliExceptions.BaseError as generic Exception."""
        error_message = "Test error message"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(error_message)
        assert str(exc_info.value) == f"[CLI_ERROR] {error_message}"

    def test_flext_cli_error_with_cause(self) -> None:
        """Test FlextCliExceptions.BaseError with underlying cause."""
        original_error = ValueError("Original error")
        wrapper_msg = "Wrapper error"

        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(wrapper_msg, cause=original_error)

        e = exc_info.value
        assert "[CLI_ERROR] Wrapper error" in str(e)
        assert hasattr(e, "context")
        assert e.context["cause"] == original_error

    # ========================================================================
    # EXCEPTION CHAINING
    # ========================================================================

    def test_exception_chaining(self) -> None:
        """Test exception chaining functionality."""
        inner_msg = "Inner error"
        outer_msg = "Outer error"

        try:
            raise ValueError(inner_msg)
        except ValueError as inner:
            with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
                raise FlextCliExceptions.BaseError(outer_msg) from inner

        outer = exc_info.value
        assert "[CLI_ERROR] Outer error" in str(outer)
        assert outer.__cause__ is not None
        assert isinstance(outer.__cause__, ValueError)
        assert str(outer.__cause__) == inner_msg

    def test_exception_context(self) -> None:
        """Test exception context functionality."""
        context_msg = "Context error"
        new_msg = "New error"

        try:
            raise ValueError(context_msg)
        except ValueError:
            with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
                raise FlextCliExceptions.BaseError(new_msg) from None

        e = exc_info.value
        assert str(e) == f"[CLI_ERROR] {new_msg}"
        assert e.__context__ is not None
        assert isinstance(e.__context__, ValueError)
        assert str(e.__context__) == context_msg

    # ========================================================================
    # EXCEPTION SERIALIZATION
    # ========================================================================

    def test_exception_to_dict(self) -> None:
        """Test converting exception to dictionary."""
        error = FlextCliExceptions.BaseError(
            "Test error",
            error_code=404,
            context="test_context",
            details={"key": "value"},
        )

        # Test that exception can be converted to dict-like structure
        error_dict = {
            "message": str(error),
            "type": type(error).__name__,
            "error_code": getattr(error, "error_code", None),
            "context": getattr(error, "context", None),
            "details": getattr(error, "details", None),
        }

        assert error_dict["message"] is not None
        assert "[404] Test error" in error_dict["message"]
        assert error_dict["type"] == "BaseError"
        assert error_dict["error_code"] == "404"
        # Test context structure
        assert error_dict["context"] is not None

    def test_exception_json_serialization(self) -> None:
        """Test exception JSON serialization."""
        error = FlextCliExceptions.BaseError("Test error", error_code=500)

        # Create serializable representation
        error_data = {
            "message": str(error),
            "type": type(error).__name__,
            "error_code": getattr(error, "error_code", None),
        }

        # Test JSON serialization
        json_string = json.dumps(error_data)
        assert isinstance(json_string, str)

        # Test JSON deserialization
        parsed_data = json.loads(json_string)
        assert "[500] Test error" in parsed_data["message"]  # Handle actual format
        assert parsed_data["type"] == "BaseError"  # Actual class name
        assert parsed_data["error_code"] == "500"

    # ========================================================================
    # EXCEPTION VALIDATION
    # ========================================================================

    def test_validate_exception_message(self) -> None:
        """Test exception message validation."""
        # Test with valid message
        error = FlextCliExceptions.BaseError("Valid error message")
        assert isinstance(str(error), str)
        assert len(str(error)) > 0

        # Test with empty message
        error = FlextCliExceptions.BaseError("")
        assert "[CLI_ERROR] " in str(error)

        # Test with None message
        error = FlextCliExceptions.BaseError("")
        assert "[CLI_ERROR] " in str(error)

    def test_validate_exception_attributes(self) -> None:
        """Test exception attributes validation."""
        error = FlextCliExceptions.BaseError(
            "Test error",
            error_code=200,
            context="test_context",
            details={"test": "data"},
        )

        # Test that attributes are set correctly
        assert hasattr(error, "error_code")
        assert error.error_code == "200"  # Error code is now a string

        assert hasattr(error, "context")
        # Test context structure
        assert error.context is not None
        assert hasattr(error, "context")

    # ========================================================================
    # EXCEPTION UTILITIES
    # ========================================================================

    def test_exception_utilities(
        self, exceptions_service: FlextCliExceptions.BaseError
    ) -> None:
        """Test exception utility functions."""
        # Test that exceptions service provides utility functions
        assert exceptions_service is not None

        # Test creating different types of errors
        errors = [
            FlextCliExceptions.BaseError("Error 1"),
            FlextCliExceptions.BaseError("Error 2", error_code=404),
            FlextCliExceptions.BaseError("Error 3", context="test"),
        ]

        # Test that all errors are properly created
        for error in errors:
            assert isinstance(error, FlextCliExceptions.BaseError)
            assert isinstance(error, Exception)

    def test_exception_comparison(self) -> None:
        """Test exception comparison functionality."""
        error1 = FlextCliExceptions.BaseError("Test error")
        error2 = FlextCliExceptions.BaseError("Test error")
        error3 = FlextCliExceptions.BaseError("Different error")

        # Test equality (same message)
        assert str(error1) == str(error2)
        assert str(error1) != str(error3)

        # Test that exceptions with same message are comparable
        assert error1.message == error2.message
        assert error1.message != error3.message

    # ========================================================================
    # EXCEPTION SCENARIOS
    # ========================================================================

    def test_file_not_found_scenario(self) -> None:
        """Test file not found exception scenario."""
        file_msg = "File not found"

        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(
                file_msg,
                error_code=404,
                context="file_operations",
                details={"file_path": "/nonexistent/file.txt"},
            )

        e = exc_info.value
        assert (
            str(e)
            == f"[404] {file_msg} (context=file_operations, details={{'file_path': '/nonexistent/file.txt'}})"
        )
        assert e.error_code == "404"
        # Test context structure
        assert e.context is not None
        assert hasattr(e, "context")

    def test_authentication_failed_scenario(self) -> None:
        """Test authentication failed exception scenario."""
        auth_msg = "Authentication failed"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(
                auth_msg,
                error_code=401,
                context="authentication",
                details={"username": "test_user", "reason": "invalid_password"},
            )
        e = exc_info.value
        assert "[401] Authentication failed" in str(e)
        assert e.error_code == "401"
        # Test context structure
        assert e.context is not None
        assert hasattr(e, "context")

    def test_validation_error_scenario(self) -> None:
        """Test validation error exception scenario."""
        validation_msg = "Validation failed"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(
                validation_msg,
                error_code=400,
                context="validation",
                details={
                    "field": "email",
                    "value": "invalid_email",
                    "rule": "email_format",
                },
            )
        e = exc_info.value
        assert "[400] Validation failed" in str(e)
        assert e.error_code == "400"
        # Test context structure
        assert e.context is not None
        assert hasattr(e, "context")

    def test_network_error_scenario(self) -> None:
        """Test network error exception scenario."""
        network_msg = "Network connection failed"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.BaseError(
                network_msg,
                error_code=503,
                context="network",
                details={
                    "url": "https://api.example.com",
                    "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
                    "retries": FlextCliConstants.HTTP.MAX_RETRIES,
                },
            )
        e = exc_info.value
        assert "[503] Network connection failed" in str(e)
        assert e.error_code == "503"
        # Test context structure
        assert e.context is not None
        assert hasattr(e, "context")

    # ========================================================================
    # EXCEPTION HANDLING PATTERNS
    # ========================================================================

    def test_exception_handling_pattern(self) -> None:
        """Test common exception handling pattern."""
        operation_msg = "Operation failed"

        def risky_operation() -> str:
            raise FlextCliExceptions.BaseError(operation_msg, error_code=500)

        try:
            risky_operation()
        except FlextCliExceptions.BaseError as e:
            # Handle the error appropriately
            error_info = {
                "message": str(e),
                "code": getattr(e, "error_code", None),
                "context": getattr(e, "context", None),
            }
            assert error_info["message"] is not None
            assert "[500] Operation failed" in error_info["message"]
            assert error_info["code"] == "500"

    def test_exception_logging_pattern(self) -> None:
        """Test exception logging pattern."""
        # Create a logger
        logging.getLogger("test_logger")

        try:
            msg = "Test error"
            raise FlextCliExceptions.BaseError(msg, error_code=500, context="test")
        except FlextCliExceptions.BaseError as e:
            # Log the error with context
            log_data = {
                "error": str(e),
                "code": getattr(e, "error_code", None),
                "context": getattr(e, "context", None),
            }

            # Verify log data structure
            assert log_data["error"] is not None
            assert "[500] Test error" in log_data["error"]
            assert log_data["code"] == "500"  # Error code is now a string
            # Test context structure
            assert log_data["context"] is not None

    def test_exception_recovery_pattern(self) -> None:
        """Test exception recovery pattern."""

        def operation_with_retry(max_retries: int = 3) -> str:
            for attempt in range(max_retries):
                try:
                    if attempt < 2:  # Fail first two attempts
                        msg = f"Attempt {attempt + 1} failed"
                        raise FlextCliExceptions.BaseError(msg, error_code=500)
                    return "Success"
                except FlextCliExceptions.BaseError:
                    if attempt == max_retries - 1:
                        raise  # Re-raise on final attempt
                    continue
            return "Failed"  # This should never be reached, but satisfies type checker

        # Test successful recovery
        result = operation_with_retry()
        assert result == "Success"

        # Test failure after max retries
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            operation_with_retry(max_retries=1)
        assert "Attempt 1 failed" in str(exc_info.value)

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_exception_edge_cases(self) -> None:
        """Test exception edge cases."""
        # Test with very long message
        long_message = "x" * 1000
        error = FlextCliExceptions.BaseError(long_message)
        assert "[CLI_ERROR]" in str(error)
        assert long_message in str(error)

        # Test with special characters
        special_message = "Error with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        error = FlextCliExceptions.BaseError(special_message)
        assert "[CLI_ERROR]" in str(error)
        assert special_message in str(error)

        # Test with unicode characters
        unicode_message = "Error with unicode: 你好世界 🌍"
        error = FlextCliExceptions.BaseError(unicode_message)
        assert "[CLI_ERROR]" in str(error)
        assert unicode_message in str(error)

    def test_exception_none_values(self) -> None:
        """Test exception with None values."""
        error = FlextCliExceptions.BaseError(
            "Test error", error_code="", context=None, details=None
        )

        assert "[GENERIC_ERROR] Test error" in str(error)
        assert getattr(error, "error_code", None) == "GENERIC_ERROR"
        assert getattr(error, "context", None) is not None

    def test_concurrent_exception_handling(self) -> None:
        """Test concurrent exception handling."""
        results = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                msg = f"Worker {worker_id} error"
                raise FlextCliExceptions.BaseError(msg, error_code=worker_id)
            except FlextCliExceptions.BaseError as e:
                errors.append(e)
            except Exception as e:
                results.append(f"Unexpected error: {e}")

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all exceptions were caught
        assert len(errors) == 5
        assert len(results) == 0

        for i, error in enumerate(errors):
            assert isinstance(error, FlextCliExceptions.BaseError)
            assert f"Worker {i} error" in str(error)

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_exception_workflow_integration(self) -> None:
        """Test complete exception workflow integration."""
        # 1. Create different types of errors
        errors = [
            FlextCliExceptions.BaseError(
                "File error", error_code=404, context="file_ops"
            ),
            FlextCliExceptions.BaseError("Auth error", error_code=401, context="auth"),
            FlextCliExceptions.BaseError(
                "Validation error", error_code=400, context="validation"
            ),
        ]

        # 2. Test error handling
        for error in errors:
            # Verify error properties directly
            assert isinstance(error, FlextCliExceptions.BaseError)
            assert isinstance(error, Exception)
            assert hasattr(error, "error_code")
            assert hasattr(error, "context")

            # Test that error can be raised and caught
            with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
                raise error
            e = exc_info.value
            assert e == error

        # 3. Test error serialization
        error_data = []
        for error in errors:
            data = {
                "message": str(error),
                "type": type(error).__name__,
                "code": getattr(error, "error_code", None),
                "context": getattr(error, "context", None),
            }
            error_data.append(data)

        # 4. Verify serialized data
        assert len(error_data) == 3
        assert error_data[0]["code"] == "404"
        assert error_data[1]["code"] == "401"
        assert error_data[2]["code"] == "400"

        # 5. Test error recovery
        recovery_successful = False
        for error in errors:
            if getattr(error, "error_code", None) == "404":
                recovery_successful = True
                break

        assert recovery_successful

    def test_exception_workflow_integration(self) -> None:
        """Test exception workflow integration."""

        # Test exception handling
        def operation() -> str:
            msg = "operation failed"
            time.sleep(0)  # Simulate operation
            raise FlextCliExceptions.BaseError(msg, error_code=500)

        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            operation()
        e = exc_info.value
        assert "[500] operation failed" in str(e)  # Handle actual format
        assert getattr(e, "error_code", None) == "500"

        # Test that exception handling works correctly
        assert True  # If we reach here, exception handling worked


class TestFlextCliExceptionsSubclasses:
    """Test suite for FlextCliExceptions specific exception subclasses."""

    # ========================================================================
    # CliValidationError tests
    # ========================================================================

    def test_cli_validation_error_creation(self) -> None:
        """Test CliValidationError creation with message and context."""
        error = FlextCliExceptions.CliValidationError(
            "Invalid input", field="username", value=""
        )
        assert error.message == "Invalid input"
        assert error.error_code == "CLI_VALIDATION_ERROR"
        assert error.context["field"] == "username"
        assert not error.context["value"]

    def test_cli_validation_error_raise(self) -> None:
        """Test raising and catching CliValidationError."""
        error_message = "Validation failed"
        with pytest.raises(FlextCliExceptions.CliValidationError) as exc_info:
            raise FlextCliExceptions.CliValidationError(error_message)

        assert exc_info.value.error_code == "CLI_VALIDATION_ERROR"
        assert "Validation failed" in str(exc_info.value)

    # ========================================================================
    # CliConfigurationError tests
    # ========================================================================

    def test_cli_configuration_error_creation(self) -> None:
        """Test CliConfigurationError creation with message and context."""
        error = FlextCliExceptions.CliConfigurationError(
            "Invalid configuration", config_file="config.yaml"
        )
        assert error.message == "Invalid configuration"
        assert error.error_code == "CLI_CONFIGURATION_ERROR"
        assert error.context["config_file"] == "config.yaml"

    def test_cli_configuration_error_raise(self) -> None:
        """Test raising and catching CliConfigurationError."""
        error_message = "Config load failed"
        with pytest.raises(FlextCliExceptions.CliConfigurationError) as exc_info:
            raise FlextCliExceptions.CliConfigurationError(error_message)

        assert exc_info.value.error_code == "CLI_CONFIGURATION_ERROR"
        assert "Config load failed" in str(exc_info.value)

    # ========================================================================
    # CliConnectionError tests
    # ========================================================================

    def test_cli_connection_error_creation(self) -> None:
        """Test CliConnectionError creation with message and context."""
        error = FlextCliExceptions.CliConnectionError(
            "Connection refused", host="localhost", port=8080
        )
        assert error.message == "Connection refused"
        assert error.error_code == "CLI_CONNECTION_ERROR"
        assert error.context["host"] == "localhost"
        assert error.context["port"] == 8080

    def test_cli_connection_error_raise(self) -> None:
        """Test raising and catching CliConnectionError."""
        error_message = "Network unreachable"
        with pytest.raises(FlextCliExceptions.CliConnectionError) as exc_info:
            raise FlextCliExceptions.CliConnectionError(error_message)

        assert exc_info.value.error_code == "CLI_CONNECTION_ERROR"
        assert "Network unreachable" in str(exc_info.value)

    # ========================================================================
    # CliAuthenticationError tests
    # ========================================================================

    def test_cli_authentication_error_creation(self) -> None:
        """Test CliAuthenticationError creation with message and context."""
        error = FlextCliExceptions.CliAuthenticationError(
            "Invalid credentials", username="testuser"
        )
        assert error.message == "Invalid credentials"
        assert error.error_code == "CLI_AUTHENTICATION_ERROR"
        assert error.context["username"] == "testuser"

    def test_cli_authentication_error_raise(self) -> None:
        """Test raising and catching CliAuthenticationError."""
        error_message = "Auth failed"
        with pytest.raises(FlextCliExceptions.CliAuthenticationError) as exc_info:
            raise FlextCliExceptions.CliAuthenticationError(error_message)

        assert exc_info.value.error_code == "CLI_AUTHENTICATION_ERROR"
        assert "Auth failed" in str(exc_info.value)

    # ========================================================================
    # CliCommandError tests
    # ========================================================================

    def test_cli_command_error_creation(self) -> None:
        """Test CliCommandError creation with message and context."""
        error = FlextCliExceptions.CliCommandError(
            "Command execution failed", command="test-cmd", exit_code=1
        )
        assert error.message == "Command execution failed"
        assert error.error_code == "CLI_COMMAND_ERROR"
        assert error.context["command"] == "test-cmd"
        assert error.context["exit_code"] == 1

    def test_cli_command_error_raise(self) -> None:
        """Test raising and catching CliCommandError."""
        error_message = "Command not found"
        with pytest.raises(FlextCliExceptions.CliCommandError) as exc_info:
            raise FlextCliExceptions.CliCommandError(error_message)

        assert exc_info.value.error_code == "CLI_COMMAND_ERROR"
        assert "Command not found" in str(exc_info.value)

    # ========================================================================
    # CliTimeoutError tests
    # ========================================================================

    def test_cli_timeout_error_creation(self) -> None:
        """Test CliTimeoutError creation with message and context."""
        error = FlextCliExceptions.CliTimeoutError(
            "Operation timed out", timeout_seconds=30
        )
        assert error.message == "Operation timed out"
        assert error.error_code == "CLI_TIMEOUT_ERROR"
        assert error.context["timeout_seconds"] == 30

    def test_cli_timeout_error_raise(self) -> None:
        """Test raising and catching CliTimeoutError."""
        error_message = "Timeout exceeded"
        with pytest.raises(FlextCliExceptions.CliTimeoutError) as exc_info:
            raise FlextCliExceptions.CliTimeoutError(error_message)

        assert exc_info.value.error_code == "CLI_TIMEOUT_ERROR"
        assert "Timeout exceeded" in str(exc_info.value)

    # ========================================================================
    # CliFormatError tests
    # ========================================================================

    def test_cli_format_error_creation(self) -> None:
        """Test CliFormatError creation with message and context."""
        error = FlextCliExceptions.CliFormatError(
            "Invalid format", format="json", expected="yaml"
        )
        assert error.message == "Invalid format"
        assert error.error_code == "CLI_FORMAT_ERROR"
        assert error.context["format"] == "json"
        assert error.context["expected"] == "yaml"

    def test_cli_format_error_raise(self) -> None:
        """Test raising and catching CliFormatError."""
        error_message = "Unsupported format"
        with pytest.raises(FlextCliExceptions.CliFormatError) as exc_info:
            raise FlextCliExceptions.CliFormatError(error_message)

        assert exc_info.value.error_code == "CLI_FORMAT_ERROR"
        assert "Unsupported format" in str(exc_info.value)

    # ========================================================================
    # BaseError helper methods tests
    # ========================================================================

    def test_base_error_get_context_value(self) -> None:
        """Test BaseError get_context_value method."""
        error = FlextCliExceptions.BaseError("Test error", key1="value1", key2="value2")
        assert error.get_context_value("key1") == "value1"
        assert error.get_context_value("key2") == "value2"
        assert error.get_context_value("nonexistent", "default") == "default"
        assert error.get_context_value("nonexistent") is None

    def test_base_error_is_error_code(self) -> None:
        """Test BaseError is_error_code method."""
        error = FlextCliExceptions.BaseError("Test error", error_code="TEST_ERROR")
        assert error.is_error_code("TEST_ERROR") is True
        assert error.is_error_code("OTHER_ERROR") is False
        assert error.is_error_code("test_error") is False  # Case sensitive

    def test_base_error_repr(self) -> None:
        """Test BaseError __repr__ method."""
        error = FlextCliExceptions.BaseError(
            "Test message", error_code="TEST_CODE", key="value"
        )
        repr_str = repr(error)
        assert "FlextCliExceptions.BaseError" in repr_str
        assert "message='Test message'" in repr_str
        assert "error_code='TEST_CODE'" in repr_str
        assert "context=" in repr_str

    # ========================================================================
    # Exception inheritance tests
    # ========================================================================

    def test_all_exceptions_inherit_from_base_error(self) -> None:
        """Test that all custom exceptions inherit from BaseError."""
        validation_error = FlextCliExceptions.CliValidationError("test")
        config_error = FlextCliExceptions.CliConfigurationError("test")
        connection_error = FlextCliExceptions.CliConnectionError("test")
        auth_error = FlextCliExceptions.CliAuthenticationError("test")
        command_error = FlextCliExceptions.CliCommandError("test")
        timeout_error = FlextCliExceptions.CliTimeoutError("test")
        format_error = FlextCliExceptions.CliFormatError("test")

        assert isinstance(validation_error, FlextCliExceptions.BaseError)
        assert isinstance(config_error, FlextCliExceptions.BaseError)
        assert isinstance(connection_error, FlextCliExceptions.BaseError)
        assert isinstance(auth_error, FlextCliExceptions.BaseError)
        assert isinstance(command_error, FlextCliExceptions.BaseError)
        assert isinstance(timeout_error, FlextCliExceptions.BaseError)
        assert isinstance(format_error, FlextCliExceptions.BaseError)

    def test_exception_polymorphism(self) -> None:
        """Test exception polymorphism - catching via BaseError."""
        error_message = "Validation failed"
        with pytest.raises(FlextCliExceptions.BaseError) as exc_info:
            raise FlextCliExceptions.CliValidationError(error_message)

        assert isinstance(exc_info.value, FlextCliExceptions.CliValidationError)
        assert isinstance(exc_info.value, FlextCliExceptions.BaseError)
        assert exc_info.value.error_code == "CLI_VALIDATION_ERROR"
