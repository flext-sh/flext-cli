"""Tests for core helpers in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from unittest.mock import patch

from rich.console import Console
from rich.prompt import Confirm, Prompt

from flext_cli import CLIHelper

# Constants
EXPECTED_BULK_SIZE = 2


class TestCLIHelper:
    """Test cases for CLIHelper class."""

    def test_helper_initialization(self) -> None:
        """Test CLIHelper initialization."""
        helper = CLIHelper()
        assert isinstance(helper.console, Console)

    def test_helper_initialization_with_console(self) -> None:
        """Test CLIHelper initialization with custom console."""
        custom_console = Console()
        helper = CLIHelper(console=custom_console)
        assert helper.console is custom_console

    def test_confirm_default_false(self) -> None:
        """Test confirm method with default False."""
        helper = CLIHelper()

        # Import and mock the Confirm.ask method

        # Test with mocked response
        with patch.object(Confirm, "ask", return_value=True):
            result = helper.confirm("Are you sure?")
            if not (result):
                raise AssertionError(f"Expected True, got {result}")

    def test_confirm_default_true(self) -> None:
        """Test confirm method with default True."""
        helper = CLIHelper()

        with patch.object(Confirm, "ask", return_value=False):
            result = helper.confirm("Are you sure?", default=True)
            if result:
                raise AssertionError(f"Expected False, got {result}")

    def test_prompt_without_default(self) -> None:
        """Test prompt method without default."""
        helper = CLIHelper()

        with patch.object(Prompt, "ask", return_value="test input"):
            result = helper.prompt("Enter name:")
            if result != "test input":
                raise AssertionError(f"Expected {'test input'}, got {result}")

    def test_prompt_with_default(self) -> None:
        """Test prompt method with default."""
        helper = CLIHelper()

        with patch.object(Prompt, "ask", return_value="default"):
            result = helper.prompt("Enter name:", default="default")
            if result != "default":
                raise AssertionError(f"Expected {'default'}, got {result}")

    def test_validate_url_valid(self) -> None:
        """Test URL validation with valid URLs."""
        helper = CLIHelper()

        if not (helper.validate_url("https://example.com")):
            raise AssertionError(
                f"Expected True, got {helper.validate_url('https://example.com')}",
            )
        assert (
            helper.validate_url(
                f"http://{__import__('flext_core.constants').flext_core.constants.FlextConstants.Platform.DEFAULT_HOST}:{__import__('flext_core.constants').flext_core.constants.FlextConstants.Platform.FLEXCORE_PORT}",
            )
            is True
        )
        if not (helper.validate_url("ftp://files.example.com")):
            raise AssertionError(
                f"Expected True, got {helper.validate_url('ftp://files.example.com')}",
            )

    def test_validate_url_invalid(self) -> None:
        """Test URL validation with invalid URLs."""
        helper = CLIHelper()

        if helper.validate_url("not-a-url"):
            raise AssertionError(
                f"Expected False, got {helper.validate_url('not-a-url')}",
            )
        assert helper.validate_url("") is False
        assert helper.validate_url("example.com") is False  # No scheme

    def test_validate_url_exception_handling(self) -> None:
        """Test URL validation with values that cause exceptions."""
        helper = CLIHelper()

        assert helper.validate_url(None) is False

    def test_validate_path_existing(self) -> None:
        """Test path validation with existing path."""
        helper = CLIHelper()

        with tempfile.NamedTemporaryFile() as tmp:
            if not (helper.validate_path(tmp.name, must_exist=True)):
                raise AssertionError(
                    f"Expected True, got {helper.validate_path(tmp.name, must_exist=True)}",
                )

    def test_validate_path_non_existing_must_exist(self) -> None:
        """Test path validation with non-existing path when must_exist=True."""
        helper = CLIHelper()

        if helper.validate_path("/non/existing/path", must_exist=True):
            raise AssertionError(
                f"Expected False, got {helper.validate_path('/non/existing/path', must_exist=True)}",
            )

    def test_validate_path_non_existing_no_requirement(self) -> None:
        """Test path validation with non-existing path when must_exist=False."""
        helper = CLIHelper()

        if not (helper.validate_path("/non/existing/path", must_exist=False)):
            raise AssertionError(
                f"Expected True, got {helper.validate_path('/non/existing/path', must_exist=False)}",
            )

    def test_validate_path_exception_handling(self) -> None:
        """Test path validation with invalid path values."""
        helper = CLIHelper()

        # Test with path that causes exception in exists() method
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.side_effect = OSError("Permission denied")
            if helper.validate_path("/some/path", must_exist=True):
                raise AssertionError(
                    f"Expected False, got {helper.validate_path('/some/path', must_exist=True)}",
                )

    def test_validate_email_valid(self) -> None:
        """Test email validation with valid emails."""
        helper = CLIHelper()

        if not (helper.validate_email("test@example.com")):
            raise AssertionError(
                f"Expected True, got {helper.validate_email('test@example.com')}",
            )
        assert helper.validate_email("user.name+tag@domain.co.uk") is True
        if not (helper.validate_email("123@456.com")):
            raise AssertionError(
                f"Expected True, got {helper.validate_email('123@456.com')}",
            )

    def test_validate_email_invalid(self) -> None:
        """Test email validation with invalid emails."""
        helper = CLIHelper()

        if helper.validate_email("not-an-email"):
            raise AssertionError(
                f"Expected False, got {helper.validate_email('not-an-email')}",
            )
        assert helper.validate_email("@example.com") is False
        if helper.validate_email("test@"):
            raise AssertionError(
                f"Expected False, got {helper.validate_email('test@')}",
            )
        assert helper.validate_email("") is False

    def test_format_size_bytes(self) -> None:
        """Test file size formatting with bytes."""
        helper = CLIHelper()

        if helper.format_size(100) != "100.0 B":
            raise AssertionError(f"Expected {'100.0 B'}, got {helper.format_size(100)}")
        assert helper.format_size(0) == "0.0 B"

    def test_format_size_kilobytes(self) -> None:
        """Test file size formatting with kilobytes."""
        helper = CLIHelper()

        if helper.format_size(1024) != "1.0 KB":
            raise AssertionError(f"Expected {'1.0 KB'}, got {helper.format_size(1024)}")
        assert helper.format_size(2048) == "2.0 KB"

    def test_format_size_megabytes(self) -> None:
        """Test file size formatting with megabytes."""
        helper = CLIHelper()

        if helper.format_size(1024 * 1024) != "1.0 MB":
            raise AssertionError(
                f"Expected {'1.0 MB'}, got {helper.format_size(1024 * 1024)}",
            )
        assert helper.format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_format_size_gigabytes(self) -> None:
        """Test file size formatting with gigabytes."""
        helper = CLIHelper()

        if helper.format_size(1024 * 1024 * 1024) != "1.0 GB":
            raise AssertionError(
                f"Expected {'1.0 GB'}, got {helper.format_size(1024 * 1024 * 1024)}",
            )

    def test_truncate_text_short(self) -> None:
        """Test text truncation with short text."""
        helper = CLIHelper()

        text = "Short text"
        if helper.truncate_text(text, max_length=50) != "Short text":
            raise AssertionError(
                f"Expected {'Short text'}, got {helper.truncate_text(text, max_length=50)}",
            )

    def test_truncate_text_long(self) -> None:
        """Test text truncation with long text."""
        helper = CLIHelper()

        text = "This is a very long text that should be truncated"
        result = helper.truncate_text(text, max_length=20)
        if len(result) != 20:
            raise AssertionError(f"Expected {20}, got {len(result)}")
        assert result.endswith("...")

    def test_truncate_text_exact_length(self) -> None:
        """Test text truncation with exact max length."""
        helper = CLIHelper()

        text = "12345"
        if helper.truncate_text(text, max_length=5) != "12345":
            raise AssertionError(
                f"Expected {'12345'}, got {helper.truncate_text(text, max_length=5)}",
            )

    def test_sanitize_filename_safe(self) -> None:
        """Test filename sanitization with safe filename."""
        helper = CLIHelper()

        if helper.sanitize_filename("safe_filename.txt") != "safe_filename.txt":
            raise AssertionError(
                f"Expected {'safe_filename.txt'}, got {helper.sanitize_filename('safe_filename.txt')}",
            )

    def test_sanitize_filename_unsafe_characters(self) -> None:
        """Test filename sanitization with unsafe characters."""
        helper = CLIHelper()

        result = helper.sanitize_filename('file<>:"/\\|?*.txt')
        if "<" in result:
            raise AssertionError(
                f"Expected '<' not in result, but found it in {result}",
            )
        assert ">" not in result
        if ":" in result:
            raise AssertionError(
                f"Expected ':' not in result, but found it in {result}",
            )
        assert '"' not in result
        if "/" in result:
            raise AssertionError(
                f"Expected '/' not in result, but found it in {result}",
            )
        assert "\\" not in result
        if "|" in result:
            raise AssertionError(
                f"Expected '|' not in result, but found it in {result}",
            )
        assert "?" not in result
        if "*" in result:
            raise AssertionError(
                f"Expected '*' not in result, but found it in {result}",
            )

    def test_sanitize_filename_dots_and_spaces(self) -> None:
        """Test filename sanitization with leading/trailing dots and spaces."""
        helper = CLIHelper()

        if helper.sanitize_filename("  .filename.  ") != "filename":
            raise AssertionError(
                f"Expected {'filename'}, got {helper.sanitize_filename('  .filename.  ')}",
            )
        assert helper.sanitize_filename("...") == "untitled"

    def test_sanitize_filename_empty(self) -> None:
        """Test filename sanitization with empty string."""
        helper = CLIHelper()

        if helper.sanitize_filename("") != "untitled":
            raise AssertionError(
                f"Expected {'untitled'}, got {helper.sanitize_filename('')}",
            )
        assert helper.sanitize_filename("   ") == "untitled"

    def test_create_progress(self) -> None:
        """Test progress bar creation."""
        helper = CLIHelper()

        progress = helper.create_progress("Loading...")
        # Should return a Progress object without errors
        assert progress is not None

    def test_print_success(self) -> None:
        """Test success message printing."""
        helper = CLIHelper()

        # Mock the console print method
        with patch.object(helper.console, "print") as mock_print:
            helper.print_success("Operation successful")
            mock_print.assert_called_once_with(
                "[bold green]✓[/bold green] Operation successful",
            )

    def test_print_error(self) -> None:
        """Test error message printing."""
        helper = CLIHelper()

        with patch.object(helper.console, "print") as mock_print:
            helper.print_error("Operation failed")
            mock_print.assert_called_once_with(
                "[bold red]✗[/bold red] Operation failed",
            )

    def test_print_warning(self) -> None:
        """Test warning message printing."""
        helper = CLIHelper()

        with patch.object(helper.console, "print") as mock_print:
            helper.print_warning("Warning message")
            mock_print.assert_called_once_with(
                "[bold yellow]⚠[/bold yellow] Warning message",
            )

    def test_print_info(self) -> None:
        """Test info message printing."""
        helper = CLIHelper()

        with patch.object(helper.console, "print") as mock_print:
            helper.print_info("Info message")
            mock_print.assert_called_once_with("[bold blue]i[/bold blue] Info message")
