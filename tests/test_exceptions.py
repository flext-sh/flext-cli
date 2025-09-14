"""FLEXT CLI Exceptions Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile

import pytest

from flext_cli import (
    FlextCliArgumentError,
    FlextCliAuthenticationError,
    FlextCliCommandError,
    FlextCliConfigurationError,
    FlextCliConnectionError,
    FlextCliContextError,
    FlextCliError,
    FlextCliException,
    FlextCliFormatError,
    FlextCliOutputError,
    FlextCliProcessingError,
    FlextCliTimeoutError,
    FlextCliValidationError,
)


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
            assert hasattr(FlextCliException.ErrorCode, attr_name)
            assert (
                getattr(FlextCliException.ErrorCode, attr_name).value == expected_value
            )


class TestFlextCliError:
    """Test base FlextCliError."""

    def test_basic_creation(self) -> None:
        """Test basic error creation."""
        error = FlextCliError("Test error message")
        assert "Test error message" in str(error)
        assert isinstance(error, Exception)

    def test_inheritance_chain(self) -> None:
        """Test inheritance from FlextExceptions."""
        error = FlextCliError("Test")
        # Should be instance of FlextCliError and its parent FlextExceptions
        assert isinstance(error, FlextCliError)


class TestFlextCliValidationError:
    """Test FlextCliValidationError."""

    def test_validation_error_creation(self) -> None:
        """Test validation error creation."""
        error = FlextCliValidationError("Validation failed")
        assert "Validation failed" in str(error)
        assert isinstance(error, FlextCliError)


class TestFlextCliConfigurationError:
    """Test FlextCliConfigurationError."""

    def test_configuration_error_creation(self) -> None:
        """Test configuration error creation."""
        error = FlextCliConfigurationError("Config error")
        assert "Config error" in str(error)
        assert isinstance(error, FlextCliError)


class TestFlextCliConnectionError:
    """Test FlextCliConnectionError."""

    def test_connection_error_creation(self) -> None:
        """Test connection error creation."""
        error = FlextCliConnectionError("Connection failed")
        assert "Connection failed" in str(error)
        assert isinstance(error, FlextCliError)


class TestFlextCliProcessingError:
    """Test FlextCliProcessingError."""

    def test_processing_error_creation(self) -> None:
        """Test processing error creation."""
        error = FlextCliProcessingError("Processing failed")
        assert "Processing failed" in str(error)
        assert isinstance(error, FlextCliError)


class TestFlextCliAuthenticationError:
    """Test FlextCliAuthenticationError."""

    def test_authentication_error_creation(self) -> None:
        """Test authentication error creation."""
        error = FlextCliAuthenticationError("Auth failed")
        assert "Auth failed" in str(error)
        assert isinstance(error, FlextCliError)


class TestFlextCliTimeoutError:
    """Test FlextCliTimeoutError."""

    def test_timeout_error_creation(self) -> None:
        """Test timeout error creation."""
        error = FlextCliTimeoutError("Operation timed out")
        assert "Operation timed out" in str(error)
        assert isinstance(error, FlextCliError)


class TestFlextCliCommandError:
    """Test FlextCliCommandError with context."""

    def test_command_error_basic(self) -> None:
        """Test basic command error creation."""
        error = FlextCliCommandError("Command failed")
        assert "Command failed" in str(error)
        assert isinstance(error, FlextCliError)

    def test_command_error_with_command(self) -> None:
        """Test command error with command context."""
        error = FlextCliCommandError("Command failed", command="echo test", exit_code=1)
        assert "Command failed" in str(error)
        # Context should be available via the FlextExceptions base class
        assert hasattr(error, "context") or hasattr(error, "_context")

    def test_command_error_with_context(self) -> None:
        """Test command error with additional context."""
        error = FlextCliCommandError(
            "Command failed",
            command="ls -la",
            exit_code=2,
            context={"user": "test", "directory": tempfile.gettempdir()},
        )
        assert "Command failed" in str(error)


class TestFlextCliArgumentError:
    """Test FlextCliArgumentError with argument context."""

    def test_argument_error_basic(self) -> None:
        """Test basic argument error creation."""
        error = FlextCliArgumentError("Invalid argument")
        assert "Invalid argument" in str(error)
        assert isinstance(error, FlextCliError)

    def test_argument_error_with_context(self) -> None:
        """Test argument error with argument details."""
        error = FlextCliArgumentError(
            "Invalid value",
            argument_name="--output",
            argument_value="invalid_format",
        )
        assert "Invalid value" in str(error)

    def test_argument_error_full_context(self) -> None:
        """Test argument error with full context."""
        error = FlextCliArgumentError(
            "Argument validation failed",
            argument_name="--count",
            argument_value="-5",
            context={"min_value": 0, "max_value": 100},
        )
        assert "Argument validation failed" in str(error)


class TestFlextCliFormatError:
    """Test FlextCliFormatError with format context."""

    def test_format_error_basic(self) -> None:
        """Test basic format error creation."""
        error = FlextCliFormatError("Format error")
        assert "Format error" in str(error)
        assert isinstance(error, FlextCliError)

    def test_format_error_with_context(self) -> None:
        """Test format error with format details."""
        error = FlextCliFormatError(
            "Unsupported format",
            format_type="xml",
            data_type="dict",
        )
        assert "Unsupported format" in str(error)

    def test_format_error_full_context(self) -> None:
        """Test format error with additional context."""
        error = FlextCliFormatError(
            "Format conversion failed",
            format_type="csv",
            data_type="nested_dict",
            context={"supported_formats": ["json", "yaml", "table"]},
        )
        assert "Format conversion failed" in str(error)


class TestFlextCliOutputError:
    """Test FlextCliOutputError with output context."""

    def test_output_error_basic(self) -> None:
        """Test basic output error creation."""
        error = FlextCliOutputError("Output error")
        assert "Output error" in str(error)
        assert isinstance(error, FlextCliError)

    def test_output_error_with_context(self) -> None:
        """Test output error with output details."""
        error = FlextCliOutputError(
            "Cannot write to file",
            output_format="json",
            output_path="/readonly/file.json",
        )
        assert "Cannot write to file" in str(error)

    def test_output_error_full_context(self) -> None:
        """Test output error with additional context."""
        error = FlextCliOutputError(
            "Output processing failed",
            output_format="csv",
            output_path=f"{tempfile.gettempdir()}/export.csv",
            context={"permissions": "read-only", "disk_space": "0MB"},
        )
        assert "Output processing failed" in str(error)


class TestFlextCliContextError:
    """Test FlextCliContextError with context state."""

    def test_context_error_basic(self) -> None:
        """Test basic context error creation."""
        error = FlextCliContextError("Context error")
        assert "Context error" in str(error)
        assert isinstance(error, FlextCliError)

    def test_context_error_with_state(self) -> None:
        """Test context error with state details."""
        error = FlextCliContextError(
            "Invalid context state",
            context_name="session_context",
            context_state="corrupted",
        )
        assert "Invalid context state" in str(error)

    def test_context_error_full_context(self) -> None:
        """Test context error with additional context."""
        error = FlextCliContextError(
            "Context initialization failed",
            context_name="cli_context",
            context_state="uninitialized",
            context={"expected_fields": ["user", "session"], "missing": ["user"]},
        )
        assert "Context initialization failed" in str(error)


class TestExceptionRaising:
    """Test that exceptions can be raised and caught properly."""

    def test_raise_and_catch_command_error(self) -> None:
        """Test raising and catching command errors."""
        msg = "Test command failed"
        with pytest.raises(FlextCliCommandError) as exc_info:
            raise FlextCliCommandError(msg, command="test_cmd")

        assert "Test command failed" in str(exc_info.value)
        assert isinstance(exc_info.value, FlextCliError)

    def test_raise_and_catch_base_error(self) -> None:
        """Test raising and catching base CLI error."""
        msg = "Base CLI error"
        with pytest.raises(FlextCliError) as exc_info:
            raise FlextCliError(msg)

        assert "Base CLI error" in str(exc_info.value)

    def test_catch_specific_with_base(self) -> None:
        """Test that specific errors can be caught as base CLI error."""
        msg = "Specific error"
        with pytest.raises(FlextCliError):  # Should catch the specific error
            raise FlextCliArgumentError(msg)
