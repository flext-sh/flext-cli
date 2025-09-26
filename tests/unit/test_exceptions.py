"""FLEXT CLI Exceptions Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliExceptions covering all real functionality with flext_tests
integration, comprehensive exception handling, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import logging
import threading

import pytest

from flext_cli.exceptions import FlextCliError, FlextCliExceptions
from flext_tests import FlextTestsUtilities


class TestFlextCliExceptions:
    """Comprehensive tests for FlextCliExceptions functionality."""

    @pytest.fixture
    def exceptions_service(self) -> FlextCliExceptions:
        """Create FlextCliExceptions instance for testing."""
        return FlextCliExceptions()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_exceptions_service_initialization(
        self, exceptions_service: FlextCliExceptions
    ) -> None:
        """Test exceptions service initialization and basic properties."""
        assert exceptions_service is not None
        assert hasattr(exceptions_service, "__class__")

    def test_exceptions_service_basic_functionality(
        self, exceptions_service: FlextCliExceptions
    ) -> None:
        """Test exceptions service basic functionality."""
        # Test that exceptions can be created and accessed
        assert exceptions_service is not None
        assert hasattr(exceptions_service, "__class__")

    # ========================================================================
    # EXCEPTION CLASS TESTING
    # ========================================================================

    def test_flext_cli_error_creation(self) -> None:
        """Test FlextCliError exception creation."""
        # Test basic exception creation
        error = FlextCliError("Test error message")
        assert isinstance(error, FlextCliError)
        assert isinstance(error, Exception)
        assert "[CLI_ERROR] Test error message" in str(error)

    def test_flext_cli_error_with_details(self) -> None:
        """Test FlextCliError with additional details."""
        error = FlextCliError("Test error", details={"code": 123, "context": "test"})
        assert isinstance(error, FlextCliError)
        assert "[CLI_ERROR] Test error" in str(error)
        assert hasattr(error, "context")
        assert error.context["details"]["code"] == 123
        assert error.context["details"]["context"] == "test"

    def test_flext_cli_error_inheritance(self) -> None:
        """Test FlextCliError inheritance chain."""
        error = FlextCliError("Test error")

        # Test inheritance
        assert isinstance(error, Exception)
        assert isinstance(error, FlextCliError)

        # Test that it can be caught as Exception
        with pytest.raises(FlextCliError) as exc_info:
            raise error
        assert "[CLI_ERROR] Test error" in str(exc_info.value)

    def test_flext_cli_error_custom_attributes(self) -> None:
        """Test FlextCliError with custom attributes."""
        error = FlextCliError(
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
        """Test raising FlextCliError exception."""
        error_message = "Test error message"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(error_message)

        assert str(exc_info.value) == "[CLI_ERROR] Test error message"
        assert isinstance(exc_info.value, FlextCliError)

    def test_catch_flext_cli_error(self) -> None:
        """Test catching FlextCliError exception."""
        error_message = "Test error message"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(error_message)

        assert str(exc_info.value) == f"[CLI_ERROR] {error_message}"
        assert isinstance(exc_info.value, FlextCliError)

    def test_catch_flext_cli_error_as_exception(self) -> None:
        """Test catching FlextCliError as generic Exception."""
        error_message = "Test error message"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(error_message)
        assert str(exc_info.value) == f"[CLI_ERROR] {error_message}"

    def test_flext_cli_error_with_cause(self) -> None:
        """Test FlextCliError with underlying cause."""
        original_error = ValueError("Original error")
        wrapper_msg = "Wrapper error"

        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(wrapper_msg, cause=original_error)

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

        with pytest.raises(FlextCliError) as exc_info:  # noqa: PT012
            try:
                raise ValueError(inner_msg)
            except ValueError as inner:
                raise FlextCliError(outer_msg) from inner

        outer = exc_info.value
        assert "[CLI_ERROR] Outer error" in str(outer)
        assert outer.__cause__ is not None
        assert isinstance(outer.__cause__, ValueError)
        assert str(outer.__cause__) == inner_msg

    def test_exception_context(self) -> None:
        """Test exception context functionality."""
        context_msg = "Context error"
        new_msg = "New error"

        with pytest.raises(FlextCliError) as exc_info:  # noqa: PT012
            try:
                raise ValueError(context_msg)
            except ValueError:
                raise FlextCliError(new_msg) from None

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
        error = FlextCliError(
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

        assert "[404] Test error" in error_dict["message"]
        assert error_dict["type"] == "_BaseError"
        assert error_dict["error_code"] == "404"
        assert error_dict["context"]["context"] == "test_context"
        assert error_dict["context"]["details"]["key"] == "value"

    def test_exception_json_serialization(self) -> None:
        """Test exception JSON serialization."""
        error = FlextCliError("Test error", error_code=500)

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
        assert parsed_data["type"] == "_BaseError"  # Actual class name
        assert parsed_data["error_code"] == "500"

    # ========================================================================
    # EXCEPTION VALIDATION
    # ========================================================================

    def test_validate_exception_message(self) -> None:
        """Test exception message validation."""
        # Test with valid message
        error = FlextCliError("Valid error message")
        assert isinstance(str(error), str)
        assert len(str(error)) > 0

        # Test with empty message
        error = FlextCliError("")
        assert "[CLI_ERROR] " in str(error)

        # Test with None message
        error = FlextCliError(None)
        assert "[CLI_ERROR] None" in str(error)

    def test_validate_exception_attributes(self) -> None:
        """Test exception attributes validation."""
        error = FlextCliError(
            "Test error",
            error_code=200,
            context="test_context",
            details={"test": "data"},
        )

        # Test that attributes are set correctly
        assert hasattr(error, "error_code")
        assert error.error_code == "200"  # Error code is now a string

        assert hasattr(error, "context")
        assert error.context["context"] == "test_context"
        assert error.context["details"]["test"] == "data"

    # ========================================================================
    # EXCEPTION UTILITIES
    # ========================================================================

    def test_exception_utilities(self, exceptions_service: FlextCliExceptions) -> None:
        """Test exception utility functions."""
        # Test that exceptions service provides utility functions
        assert exceptions_service is not None

        # Test creating different types of errors
        errors = [
            FlextCliError("Error 1"),
            FlextCliError("Error 2", error_code=404),
            FlextCliError("Error 3", context="test"),
        ]

        # Test that all errors are properly created
        for error in errors:
            assert isinstance(error, FlextCliError)
            assert isinstance(error, Exception)

    def test_exception_comparison(self) -> None:
        """Test exception comparison functionality."""
        error1 = FlextCliError("Test error")
        error2 = FlextCliError("Test error")
        error3 = FlextCliError("Different error")

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

        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(
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
        assert e.context["context"] == "file_operations"
        assert e.context["details"]["file_path"] == "/nonexistent/file.txt"

    def test_authentication_failed_scenario(self) -> None:
        """Test authentication failed exception scenario."""
        auth_msg = "Authentication failed"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(
                auth_msg,
                error_code=401,
                context="authentication",
                details={"username": "test_user", "reason": "invalid_password"},
            )
        e = exc_info.value
        assert "[401] Authentication failed" in str(e)
        assert e.error_code == "401"
        assert e.context["context"] == "authentication"
        assert e.context["details"]["username"] == "test_user"
        assert e.context["details"]["reason"] == "invalid_password"

    def test_validation_error_scenario(self) -> None:
        """Test validation error exception scenario."""
        validation_msg = "Validation failed"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(
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
        assert e.context["context"] == "validation"
        assert e.context["details"]["field"] == "email"
        assert e.context["details"]["value"] == "invalid_email"
        assert e.context["details"]["rule"] == "email_format"

    def test_network_error_scenario(self) -> None:
        """Test network error exception scenario."""
        network_msg = "Network connection failed"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(
                network_msg,
                error_code=503,
                context="network",
                details={"url": "https://api.example.com", "timeout": 30, "retries": 3},
            )
        e = exc_info.value
        assert "[503] Network connection failed" in str(e)
        assert e.error_code == "503"
        assert e.context["context"] == "network"
        assert e.context["details"]["url"] == "https://api.example.com"
        assert e.context["details"]["timeout"] == 30
        assert e.context["details"]["retries"] == 3

    # ========================================================================
    # EXCEPTION HANDLING PATTERNS
    # ========================================================================

    def test_exception_handling_pattern(self) -> None:
        """Test common exception handling pattern."""
        operation_msg = "Operation failed"

        def risky_operation() -> str:
            raise FlextCliError(operation_msg, error_code=500)

        try:
            risky_operation()
        except FlextCliError as e:
            # Handle the error appropriately
            error_info = {
                "message": str(e),
                "code": getattr(e, "error_code", None),
                "context": getattr(e, "context", None),
            }
            assert "[500] Operation failed" in error_info["message"]
            assert error_info["code"] == "500"

    def test_exception_logging_pattern(self) -> None:
        """Test exception logging pattern."""
        # Create a logger
        logging.getLogger("test_logger")

        try:
            msg = "Test error"
            raise FlextCliError(msg, error_code=500, context="test")
        except FlextCliError as e:
            # Log the error with context
            log_data = {
                "error": str(e),
                "code": getattr(e, "error_code", None),
                "context": getattr(e, "context", None),
            }

            # Verify log data structure
            assert "[500] Test error" in log_data["error"]  # Handle actual format
            assert log_data["code"] == "500"  # Error code is now a string
            assert log_data["context"]["context"] == "test"

    def test_exception_recovery_pattern(self) -> None:
        """Test exception recovery pattern."""

        def operation_with_retry(max_retries: int = 3) -> str:
            for attempt in range(max_retries):
                try:
                    if attempt < 2:  # Fail first two attempts
                        raise FlextCliError(
                            f"Attempt {attempt + 1} failed", error_code=500
                        )
                    return "Success"
                except FlextCliError:
                    if attempt == max_retries - 1:
                        raise  # Re-raise on final attempt
                    continue
            return "Failed"  # This should never be reached, but satisfies type checker

        # Test successful recovery
        result = operation_with_retry()
        assert result == "Success"

        # Test failure after max retries
        with pytest.raises(FlextCliError) as exc_info:
            operation_with_retry(max_retries=1)
        assert "Attempt 1 failed" in str(exc_info.value)

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_exception_edge_cases(self) -> None:
        """Test exception edge cases."""
        # Test with very long message
        long_message = "x" * 1000
        error = FlextCliError(long_message)
        assert "[CLI_ERROR]" in str(error) and long_message in str(error)

        # Test with special characters
        special_message = "Error with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        error = FlextCliError(special_message)
        assert "[CLI_ERROR]" in str(error) and special_message in str(error)

        # Test with unicode characters
        unicode_message = "Error with unicode: 你好世界 🌍"
        error = FlextCliError(unicode_message)
        assert "[CLI_ERROR]" in str(error) and unicode_message in str(error)

    def test_exception_none_values(self) -> None:
        """Test exception with None values."""
        error = FlextCliError("Test error", error_code=None, context=None, details=None)

        assert "[GENERIC_ERROR] Test error" in str(error)
        assert getattr(error, "error_code", None) == "GENERIC_ERROR"
        assert getattr(error, "context", None) is not None

    def test_concurrent_exception_handling(self) -> None:
        """Test concurrent exception handling."""
        results = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                raise FlextCliError(f"Worker {worker_id} error", error_code=worker_id)
            except FlextCliError as e:
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
            assert isinstance(error, FlextCliError)
            assert f"Worker {i} error" in str(error)

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_exception_workflow_integration(self) -> None:
        """Test complete exception workflow integration."""
        # 1. Create different types of errors
        errors = [
            FlextCliError("File error", error_code=404, context="file_ops"),
            FlextCliError("Auth error", error_code=401, context="auth"),
            FlextCliError("Validation error", error_code=400, context="validation"),
        ]

        # 2. Test error handling
        for error in errors:
            # Verify error properties directly
            assert isinstance(error, FlextCliError)
            assert isinstance(error, Exception)
            assert hasattr(error, "error_code")
            assert hasattr(error, "context")

            # Test that error can be raised and caught
            with pytest.raises(FlextCliError) as exc_info:
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

    @pytest.mark.asyncio
    async def test_async_exception_workflow_integration(self) -> None:
        """Test async exception workflow integration."""

        # Test async exception handling
        async def async_operation() -> str:  # noqa: RUF029
            msg = "Async operation failed"
            raise FlextCliError(msg, error_code=500)

        with pytest.raises(FlextCliError) as exc_info:
            await async_operation()
        e = exc_info.value
        assert "[500] Async operation failed" in str(e)  # Handle actual format
        assert getattr(e, "error_code", None) == "500"

        # Test that async exception handling works correctly
        assert True  # If we reach here, async exception handling worked
