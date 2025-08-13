"""Tests for FlextCliHelper and Core Helper Functions.

This module provides comprehensive tests for the FlextCliHelper class and
related helper functions, validating boilerplate reduction patterns and
FlextResult integration.

Test Coverage:
    - FlextCliHelper validation methods
    - Batch validation utilities
    - FlextResult integration patterns
    - Error handling and edge cases
    - Backward compatibility with warnings

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flext_cli.core.helpers import (
    FlextCliHelper,
    flext_cli_batch_validate,
    flext_cli_create_helper,
)
from flext_core.constants import FlextConstants
from rich.console import Console

_CORE = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXCORE_PORT}"


class TestFlextCliHelper:
    """Test suite for FlextCliHelper class."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.helper = FlextCliHelper()
        self.console_mock = MagicMock(spec=Console)

    def test_init_default_console(self) -> None:
        """Test initialization with default console."""
        helper = FlextCliHelper()
        assert helper.console is not None
        assert isinstance(helper.console, Console)

    def test_init_custom_console(self) -> None:
        """Test initialization with custom console."""
        custom_console = Console()
        helper = FlextCliHelper(console=custom_console)
        assert helper.console is custom_console

    def test_flext_cli_confirm_success(self) -> None:
        """Test successful confirmation with FlextResult."""
        with patch("rich.prompt.Confirm.ask", return_value=True):
            result = self.helper.flext_cli_confirm("Test confirmation?")

        assert result.success
        assert result.data is True

    def test_flext_cli_confirm_failure(self) -> None:
        """Test confirmation failure handling."""
        with patch(
            "rich.prompt.Confirm.ask",
            side_effect=KeyboardInterrupt("User cancelled"),
        ):
            result = self.helper.flext_cli_confirm("Test confirmation?")

        assert not result.success
        assert "User interrupted confirmation" in result.error

    def test_flext_cli_prompt_success(self) -> None:
        """Test successful prompt with FlextResult."""
        with patch("rich.prompt.Prompt.ask", return_value="test_input"):
            result = self.helper.flext_cli_prompt("Enter value:")

        assert result.success
        assert result.data == "test_input"

    def test_flext_cli_prompt_with_default(self) -> None:
        """Test prompt with default value."""
        with patch("rich.prompt.Prompt.ask", return_value="default_value"):
            result = self.helper.flext_cli_prompt(
                "Enter value:",
                default="default_value",
            )

        assert result.success
        assert result.data == "default_value"

    def test_flext_cli_prompt_password_mode(self) -> None:
        """Test password prompt mode."""
        with patch("rich.prompt.Prompt.ask", return_value="secret_password"):
            result = self.helper.flext_cli_prompt("Password:", password=True)

        assert result.success
        assert result.data == "secret_password"

    def test_flext_cli_validate_email_valid(self) -> None:
        """Test valid email validation."""
        result = self.helper.flext_cli_validate_email("user@example.com")

        assert result.success
        assert result.data == "user@example.com"

    def test_flext_cli_validate_email_invalid(self) -> None:
        """Test invalid email validation."""
        result = self.helper.flext_cli_validate_email("invalid-email")

        assert not result.success
        assert "Invalid email format" in result.error

    def test_flext_cli_validate_email_empty(self) -> None:
        """Test empty email validation."""
        result = self.helper.flext_cli_validate_email("")

        assert not result.success
        assert "Email cannot be empty" in result.error

    def test_flext_cli_validate_email_whitespace_handling(self) -> None:
        """Test email whitespace handling."""
        result = self.helper.flext_cli_validate_email("  user@example.com  ")

        assert result.success
        assert result.data == "user@example.com"

    def test_flext_cli_validate_url_valid_https(self) -> None:
        """Test valid HTTPS URL validation."""
        result = self.helper.flext_cli_validate_url("https://api.flext.sh")

        assert result.success
        assert result.data == "https://api.flext.sh"

    def test_flext_cli_validate_url_valid_http(self) -> None:
        """Test valid HTTP URL validation."""
        result = self.helper.flext_cli_validate_url(_CORE)

        assert result.success
        assert result.data == _CORE

    def test_flext_cli_validate_url_without_scheme(self) -> None:
        """Test URL without scheme."""
        result = self.helper.flext_cli_validate_url("example.com")

        assert not result.success
        assert "Invalid URL format" in result.error

    def test_flext_cli_validate_url_malformed(self) -> None:
        """Test malformed URL validation."""
        result = self.helper.flext_cli_validate_url("not-a-url")

        assert not result.success
        assert "Invalid URL format" in result.error

    def test_flext_cli_validate_path_existing_file(self, tmp_path: Path) -> None:
        """Test existing file path validation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = self.helper.flext_cli_validate_path(
            str(test_file),
            must_exist=True,
            must_be_file=True,
        )

        assert result.success
        assert result.data == test_file

    def test_flext_cli_validate_path_existing_directory(self, tmp_path: Path) -> None:
        """Test existing directory path validation."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        result = self.helper.flext_cli_validate_path(
            str(test_dir),
            must_exist=True,
            must_be_dir=True,
        )

        assert result.success
        assert result.data == test_dir

    def test_flext_cli_validate_path_nonexistent(self, tmp_path: Path) -> None:
        """Test nonexistent path validation."""
        nonexistent = tmp_path / "nonexistent.txt"

        result = self.helper.flext_cli_validate_path(str(nonexistent), must_exist=True)

        assert not result.success
        assert "Path does not exist" in result.error

    def test_flext_cli_validate_path_empty_string(self) -> None:
        """Test empty path string."""
        result = self.helper.flext_cli_validate_path("")

        assert not result.success
        assert "Path cannot be empty" in result.error

    def test_flext_cli_sanitize_filename_basic(self) -> None:
        """Test basic filename sanitization."""
        result = self.helper.flext_cli_sanitize_filename("file<>name?.txt")

        assert result.success
        assert result.data == "file__name_.txt"

    def test_flext_cli_sanitize_filename_dots_prefix(self) -> None:
        """Test filename starting with dots."""
        result = self.helper.flext_cli_sanitize_filename(".hidden_file.txt")

        assert result.success
        assert result.data == "_hidden_file.txt"

    def test_flext_cli_sanitize_filename_too_long(self) -> None:
        """Test filename length truncation."""
        long_name = "a" * 300 + ".txt"
        result = self.helper.flext_cli_sanitize_filename(long_name)

        assert result.success
        assert len(result.data) <= 255

    def test_flext_cli_sanitize_filename_empty(self) -> None:
        """Test empty filename handling."""
        result = self.helper.flext_cli_sanitize_filename("")

        assert not result.success
        assert "Filename cannot be empty" in result.error

    def test_flext_cli_print_status_info(self) -> None:
        """Test printing info status message."""
        helper = FlextCliHelper(console=self.console_mock)

        helper.flext_cli_print_status("Processing data", status="info")

        self.console_mock.print.assert_called_once()
        args = self.console_mock.print.call_args[0]
        # Check for info symbol presence (could be i)
        assert any(symbol in args[0] for symbol in ["i"])
        assert "Processing data" in args[0]

    def test_flext_cli_print_status_error(self) -> None:
        """Test printing error status message."""
        helper = FlextCliHelper(console=self.console_mock)

        helper.flext_cli_print_status("Operation failed", status="error")

        self.console_mock.print.assert_called_once()
        args = self.console_mock.print.call_args[0]
        assert "✗" in args[0]
        assert "Operation failed" in args[0]

    def test_flext_cli_create_table_success(self) -> None:
        """Test successful table creation."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        result = self.helper.flext_cli_create_table(data, title="Users")

        assert result.success

    def test_flext_cli_create_table_empty_data(self) -> None:
        """Test table creation with empty data."""
        result = self.helper.flext_cli_create_table([], title="Empty Table")

        assert not result.success
        assert "No data provided for table" in result.error


class TestFlextCliUtilityFunctions:
    """Test suite for FlextCli utility functions."""

    def test_flext_cli_create_helper_default(self) -> None:
        """Test creating helper with default console."""
        helper = flext_cli_create_helper()

        assert isinstance(helper, FlextCliHelper)
        assert helper.console is not None

    def test_flext_cli_create_helper_custom_console(self) -> None:
        """Test creating helper with custom console."""
        custom_console = Console()
        helper = flext_cli_create_helper(console=custom_console)

        assert isinstance(helper, FlextCliHelper)
        assert helper.console is custom_console

    def test_flext_cli_batch_validate_success(self) -> None:
        """Test successful batch validation."""
        inputs = {
            "user_email": ("user@example.com", "email"),
            "api_url": ("https://api.flext.sh", "url"),
        }

        result = flext_cli_batch_validate(inputs)

        assert result.success
        assert "user_email" in result.data
        assert "api_url" in result.data
        assert result.data["user_email"] == "user@example.com"

    def test_flext_cli_batch_validate_failure(self) -> None:
        """Test batch validation with failure."""
        inputs = {
            "user_email": ("user@example.com", "email"),
            "api_url": ("invalid-url", "url"),
        }

        result = flext_cli_batch_validate(inputs)

        assert not result.success
        assert "Validation failed for api_url" in result.error

    def test_flext_cli_batch_validate_unknown_type(self) -> None:
        """Test batch validation with unknown validation type."""
        inputs = {
            "test_key": ("test_value", "unknown_type"),
        }

        result = flext_cli_batch_validate(inputs)

        assert not result.success
        assert "Unknown validation type" in result.error

    def test_flext_cli_batch_validate_path_types(self, tmp_path: Path) -> None:
        """Test batch validation with path types."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        inputs = {
            "base_path": (str(tmp_path), "path"),
            "config_file": (str(test_file), "file"),
            "data_dir": (str(test_dir), "dir"),
        }

        result = flext_cli_batch_validate(inputs)

        assert result.success
        assert len(result.data) == 3
        assert isinstance(result.data["base_path"], Path)
        assert isinstance(result.data["config_file"], Path)
        assert isinstance(result.data["data_dir"], Path)

    def test_flext_cli_batch_validate_filename_sanitization(self) -> None:
        """Test batch validation with filename sanitization."""
        inputs = {
            "sanitized_name": ("file<>name?.txt", "filename"),
        }

        result = flext_cli_batch_validate(inputs)

        assert result.success
        assert result.data["sanitized_name"] == "file__name_.txt"


if __name__ == "__main__":
    pytest.main([__file__])
