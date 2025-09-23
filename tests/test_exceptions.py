"""FLEXT CLI Exceptions Tests - Real API only.

Tests exception handling using actual FlextCliError and FlextCliConstants.ErrorCodes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile

import pytest

from flext_cli import FlextCliConstants, FlextCliError


class TestFlextCliErrorCodes:
    """Test FlextCliConstants.ErrorCodes enum - actual API."""

    def test_error_codes_exist(self) -> None:
        """Test all actual error codes are defined in ErrorCodes."""
        assert hasattr(FlextCliConstants, "ErrorCodes")

        # Test actual error codes from real API
        assert hasattr(FlextCliConstants.ErrorCodes, "CLI_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "VALIDATION_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "CONFIGURATION_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "CONNECTION_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "AUTHENTICATION_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "COMMAND_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "TIMEOUT_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "FORMAT_ERROR")

    def test_error_code_values(self) -> None:
        """Test error code enum values match implementation."""
        assert FlextCliConstants.ErrorCodes.CLI_ERROR.value == "CLI_ERROR"
        assert FlextCliConstants.ErrorCodes.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert (
            FlextCliConstants.ErrorCodes.CONFIGURATION_ERROR.value
            == "CONFIGURATION_ERROR"
        )
        assert FlextCliConstants.ErrorCodes.CONNECTION_ERROR.value == "CONNECTION_ERROR"
        assert (
            FlextCliConstants.ErrorCodes.AUTHENTICATION_ERROR.value
            == "AUTHENTICATION_ERROR"
        )
        assert FlextCliConstants.ErrorCodes.COMMAND_ERROR.value == "COMMAND_ERROR"
        assert FlextCliConstants.ErrorCodes.TIMEOUT_ERROR.value == "TIMEOUT_ERROR"
        assert FlextCliConstants.ErrorCodes.FORMAT_ERROR.value == "FORMAT_ERROR"


class TestFlextCliError:
    """Test base FlextCliError - actual API."""

    def test_basic_creation(self) -> None:
        """Test basic error creation."""
        error = FlextCliError("Test error message")
        assert "Test error message" in str(error)
        assert isinstance(error, Exception)

    def test_inheritance_chain(self) -> None:
        """Test inheritance from base Exception."""
        error = FlextCliError("Test")
        assert isinstance(error, FlextCliError)
        assert isinstance(error, Exception)

    def test_error_code_default(self) -> None:
        """Test default error code is CLI_ERROR."""
        error = FlextCliError("Test")
        assert error.error_code == "CLI_ERROR"

    def test_error_code_custom(self) -> None:
        """Test custom error code using string value."""
        error = FlextCliError("Test", error_code="VALIDATION_ERROR")
        assert error.error_code == "VALIDATION_ERROR"

    def test_context_storage(self) -> None:
        """Test context is stored correctly."""
        error = FlextCliError("Test", context_key="value", user="test")
        assert error.context["context_key"] == "value"
        assert error.context["user"] == "test"

    def test_string_representation(self) -> None:
        """Test string representation includes error code and context."""
        error = FlextCliError(
            "Test message", error_code="VALIDATION_ERROR", key="value"
        )
        error_str = str(error)
        assert "VALIDATION_ERROR" in error_str
        assert "Test message" in error_str
        assert "key=value" in error_str

    def test_repr_representation(self) -> None:
        """Test repr includes all details."""
        error = FlextCliError("Test", user="test")
        repr_str = repr(error)
        assert "FlextCliError" in repr_str
        assert "Test" in repr_str
        assert "CLI_ERROR" in repr_str


class TestFlextCliErrorFactoryMethods:
    """Test FlextCliError factory methods - actual API."""

    def test_validation_error_creation(self) -> None:
        """Test validation error factory method."""
        error = FlextCliError.validation_error("Validation failed")
        assert "Validation failed" in str(error)
        assert error.error_code == "VALIDATION_ERROR"
        assert isinstance(error, FlextCliError)

    def test_configuration_error_creation(self) -> None:
        """Test configuration error factory method."""
        error = FlextCliError.configuration_error("Config error")
        assert "Config error" in str(error)
        assert error.error_code == "CONFIGURATION_ERROR"
        assert isinstance(error, FlextCliError)

    def test_connection_error_creation(self) -> None:
        """Test connection error factory method."""
        error = FlextCliError.connection_error("Connection failed")
        assert "Connection failed" in str(error)
        assert error.error_code == "CONNECTION_ERROR"
        assert isinstance(error, FlextCliError)

    def test_authentication_error_creation(self) -> None:
        """Test authentication error factory method."""
        error = FlextCliError.authentication_error("Auth failed")
        assert "Auth failed" in str(error)
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert isinstance(error, FlextCliError)

    def test_timeout_error_creation(self) -> None:
        """Test timeout error factory method."""
        error = FlextCliError.timeout_error("Operation timed out")
        assert "Operation timed out" in str(error)
        assert error.error_code == "TIMEOUT_ERROR"
        assert isinstance(error, FlextCliError)

    def test_command_error_creation(self) -> None:
        """Test command error factory method."""
        error = FlextCliError.command_error("Command failed")
        assert "Command failed" in str(error)
        assert error.error_code == "COMMAND_ERROR"
        assert isinstance(error, FlextCliError)

    def test_format_error_creation(self) -> None:
        """Test format error factory method."""
        error = FlextCliError.format_error("Format error")
        assert "Format error" in str(error)
        assert error.error_code == "FORMAT_ERROR"
        assert isinstance(error, FlextCliError)


class TestFlextCliErrorWithContext:
    """Test FlextCliError with context information - actual API."""

    def test_command_error_with_command_context(self) -> None:
        """Test command error with command context."""
        error = FlextCliError.command_error(
            "Command failed",
            command="echo test",
            exit_code=1,
        )
        assert "Command failed" in str(error)
        assert error.get_context_value("command") == "echo test"
        assert error.get_context_value("exit_code") == 1

    def test_command_error_with_complex_context(self) -> None:
        """Test command error with additional context."""
        error = FlextCliError.command_error(
            "Command failed",
            command="ls -la",
            exit_code=2,
            user="test",
            directory=tempfile.gettempdir(),
        )
        assert "Command failed" in str(error)
        assert error.get_context_value("command") == "ls -la"
        assert error.get_context_value("exit_code") == 2
        assert error.get_context_value("user") == "test"

    def test_validation_error_with_field_context(self) -> None:
        """Test validation error with field details."""
        error = FlextCliError.validation_error(
            "Invalid value",
            field="username",
            value="invalid@value",
            expected="alphanumeric",
        )
        assert "Invalid value" in str(error)
        assert error.get_context_value("field") == "username"
        assert error.get_context_value("value") == "invalid@value"
        assert error.get_context_value("expected") == "alphanumeric"

    def test_format_error_with_format_context(self) -> None:
        """Test format error with format details."""
        error = FlextCliError.format_error(
            "Format error",
            format_type="json",
            input_data={"key": "value"},
            position=42,
        )
        assert "Format error" in str(error)
        assert error.get_context_value("format_type") == "json"
        assert error.get_context_value("input_data") == {"key": "value"}
        assert error.get_context_value("position") == 42

    def test_context_with_default_value(self) -> None:
        """Test get_context_value with default value."""
        error = FlextCliError("Test", key="value")
        assert error.get_context_value("key") == "value"
        assert error.get_context_value("missing_key", "default") == "default"
        assert error.get_context_value("missing_key") is None


class TestFlextCliErrorChecking:
    """Test FlextCliError error code checking methods - actual API."""

    def test_is_error_code_validation(self) -> None:
        """Test is_error_code method for validation errors."""
        error = FlextCliError.validation_error("Test")
        assert error.is_error_code("VALIDATION_ERROR")
        assert not error.is_error_code("CONNECTION_ERROR")

    def test_is_error_code_authentication(self) -> None:
        """Test is_error_code method for authentication errors."""
        error = FlextCliError.authentication_error("Test")
        assert error.is_error_code("AUTHENTICATION_ERROR")
        assert not error.is_error_code("VALIDATION_ERROR")

    def test_is_error_code_command(self) -> None:
        """Test is_error_code method for command errors."""
        error = FlextCliError.command_error("Test")
        assert error.is_error_code("COMMAND_ERROR")
        assert not error.is_error_code("TIMEOUT_ERROR")


class TestFlextCliErrorIntegration:
    """Test FlextCliError integration scenarios - actual API."""

    def test_exception_catching_basic(self) -> None:
        """Test catching FlextCliError exceptions."""
        error_msg = "Test command error"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError.command_error(error_msg, command="test_cmd")

        error = exc_info.value
        assert error.is_error_code("COMMAND_ERROR")
        assert error.get_context_value("command") == "test_cmd"

    def test_exception_catching_validation(self) -> None:
        """Test catching specific validation errors."""
        msg = "Invalid input provided"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError.validation_error(msg)

        error = exc_info.value
        assert str(error) == f"[VALIDATION_ERROR] {msg}"
        assert error.is_error_code("VALIDATION_ERROR")

    def test_exception_inheritance(self) -> None:
        """Test that FlextCliError maintains inheritance."""
        error = FlextCliError.timeout_error("Test")
        assert isinstance(error, FlextCliError)
        assert isinstance(error, Exception)

    def test_error_chaining(self) -> None:
        """Test error chaining with context preservation."""
        try:
            original_msg = "Original error"
            raise ValueError(original_msg)
        except ValueError as original:
            cli_error = FlextCliError.command_error(
                "Command processing failed",
                original_error=str(original),
                command="process_data",
            )

            assert "Command processing failed" in str(cli_error)
            assert cli_error.get_context_value("original_error") == "Original error"
            assert cli_error.get_context_value("command") == "process_data"
