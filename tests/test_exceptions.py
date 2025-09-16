"""FLEXT CLI Exceptions Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile

import pytest

from flext_cli import FlextCliError


class TestFlextCliErrorCodes:
    """Test FlextCliErrorCodes enum."""

    def test_error_codes_exist(self) -> None:
        """Test all error codes are defined."""
        # Map expected values to actual attribute names
        expected_codes = {
            "CLI_ERROR": "CLI_ERROR",
            "CLI_VALIDATION_ERROR": "VALIDATION_ERROR",
            "CLI_CONFIGURATION_ERROR": "CONFIGURATION_ERROR",
            "CLI_CONNECTION_ERROR": "CONNECTION_ERROR",
            "CLI_PROCESSING_ERROR": "PROCESSING_ERROR",
            "CLI_AUTHENTICATION_ERROR": "AUTHENTICATION_ERROR",
            "CLI_TIMEOUT_ERROR": "TIMEOUT_ERROR",
            "CLI_COMMAND_ERROR": "COMMAND_ERROR",
            "CLI_ARGUMENT_ERROR": "ARGUMENT_ERROR",
            "CLI_FORMAT_ERROR": "FORMAT_ERROR",
            "CLI_OUTPUT_ERROR": "OUTPUT_ERROR",
            "CLI_CONTEXT_ERROR": "CONTEXT_ERROR",
        }

        for expected_value, attr_name in expected_codes.items():
            assert hasattr(FlextCliError.ErrorCode, attr_name)
            assert (
                getattr(FlextCliError.ErrorCode, attr_name).value == expected_value
            )


class TestFlextCliError:
    """Test base FlextCliError."""

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
        """Test default error code."""
        error = FlextCliError("Test")
        assert error.error_code == FlextCliError.ErrorCode.CLI_ERROR

    def test_error_code_custom(self) -> None:
        """Test custom error code."""
        error = FlextCliError(
            "Test",
            error_code=FlextCliError.ErrorCode.VALIDATION_ERROR,
        )
        assert error.error_code == FlextCliError.ErrorCode.VALIDATION_ERROR

    def test_context_storage(self) -> None:
        """Test context is stored correctly."""
        error = FlextCliError("Test", context_key="value", user="test")
        assert error.context["context_key"] == "value"
        assert error.context["user"] == "test"

    def test_string_representation(self) -> None:
        """Test string representation includes error code and context."""
        error = FlextCliError(
            "Test message",
            error_code=FlextCliError.ErrorCode.VALIDATION_ERROR,
            key="value",
        )
        error_str = str(error)
        assert "CLI_VALIDATION_ERROR" in error_str
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
    """Test FlextCliError factory methods."""

    def test_validation_error_creation(self) -> None:
        """Test validation error factory method."""
        error = FlextCliError.validation_error("Validation failed")
        assert "Validation failed" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.VALIDATION_ERROR
        assert isinstance(error, FlextCliError)

    def test_configuration_error_creation(self) -> None:
        """Test configuration error factory method."""
        error = FlextCliError.configuration_error("Config error")
        assert "Config error" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.CONFIGURATION_ERROR
        assert isinstance(error, FlextCliError)

    def test_connection_error_creation(self) -> None:
        """Test connection error factory method."""
        error = FlextCliError.connection_error("Connection failed")
        assert "Connection failed" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.CONNECTION_ERROR
        assert isinstance(error, FlextCliError)

    def test_authentication_error_creation(self) -> None:
        """Test authentication error factory method."""
        error = FlextCliError.authentication_error("Auth failed")
        assert "Auth failed" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.AUTHENTICATION_ERROR
        assert isinstance(error, FlextCliError)

    def test_timeout_error_creation(self) -> None:
        """Test timeout error factory method."""
        error = FlextCliError.timeout_error("Operation timed out")
        assert "Operation timed out" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.TIMEOUT_ERROR
        assert isinstance(error, FlextCliError)

    def test_command_error_creation(self) -> None:
        """Test command error factory method."""
        error = FlextCliError.command_error("Command failed")
        assert "Command failed" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.COMMAND_ERROR
        assert isinstance(error, FlextCliError)

    def test_format_error_creation(self) -> None:
        """Test format error factory method."""
        error = FlextCliError.format_error("Format error")
        assert "Format error" in str(error)
        assert error.error_code == FlextCliError.ErrorCode.FORMAT_ERROR
        assert isinstance(error, FlextCliError)


class TestFlextCliErrorWithContext:
    """Test FlextCliError with context information."""

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
    """Test FlextCliError error code checking methods."""

    def test_is_error_code_validation(self) -> None:
        """Test is_error_code method for validation errors."""
        error = FlextCliError.validation_error("Test")
        assert error.is_error_code(FlextCliError.ErrorCode.VALIDATION_ERROR)
        assert not error.is_error_code(FlextCliError.ErrorCode.CONNECTION_ERROR)

    def test_is_error_code_authentication(self) -> None:
        """Test is_error_code method for authentication errors."""
        error = FlextCliError.authentication_error("Test")
        assert error.is_error_code(FlextCliError.ErrorCode.AUTHENTICATION_ERROR)
        assert not error.is_error_code(FlextCliError.ErrorCode.VALIDATION_ERROR)

    def test_is_error_code_command(self) -> None:
        """Test is_error_code method for command errors."""
        error = FlextCliError.command_error("Test")
        assert error.is_error_code(FlextCliError.ErrorCode.COMMAND_ERROR)
        assert not error.is_error_code(FlextCliError.ErrorCode.TIMEOUT_ERROR)


class TestFlextCliErrorIntegration:
    """Test FlextCliError integration scenarios."""

    def test_exception_catching_basic(self) -> None:
        """Test catching FlextCliError exceptions."""
        error_msg = "Test command error"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError.command_error(error_msg, command="test_cmd")

        error = exc_info.value
        assert error.is_error_code(FlextCliError.ErrorCode.COMMAND_ERROR)
        assert error.get_context_value("command") == "test_cmd"

    def test_exception_catching_validation(self) -> None:
        """Test catching specific validation errors."""
        msg = "Invalid input provided"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError.validation_error(msg)

        error = exc_info.value
        assert str(error) == f"[CLI_VALIDATION_ERROR] {msg}"
        assert error.is_error_code(FlextCliError.ErrorCode.VALIDATION_ERROR)

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
            # Chain the error with additional CLI context
            cli_error = FlextCliError.command_error(
                "Command processing failed",
                original_error=str(original),
                command="process_data",
            )

            assert "Command processing failed" in str(cli_error)
            assert cli_error.get_context_value("original_error") == "Original error"
            assert cli_error.get_context_value("command") == "process_data"
