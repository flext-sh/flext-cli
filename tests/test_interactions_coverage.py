"""Test coverage for FlextCliInteractions module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import pytest
from unittest.mock import patch, MagicMock

from flext_cli.interactions import FlextCliInteractions
from flext_core import FlextResult


class TestFlextCliInteractions:
    """Test FlextCliInteractions class."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.interactions = FlextCliInteractions()

    def test_interactions_initialization(self) -> None:
        """Test interactions initialization."""
        interactions = FlextCliInteractions()
        assert interactions is not None
        assert hasattr(interactions, '_logger')
        assert hasattr(interactions, 'quiet')
        assert interactions.quiet is False

    def test_interactions_initialization_with_logger(self) -> None:
        """Test interactions initialization with custom logger."""
        mock_logger = MagicMock()
        interactions = FlextCliInteractions(logger=mock_logger)
        assert interactions._logger is mock_logger

    def test_interactions_initialization_quiet(self) -> None:
        """Test interactions initialization with quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        assert interactions.quiet is True

    @patch('builtins.input')
    def test_confirm_default_false(self, mock_input: MagicMock) -> None:
        """Test confirm with default False."""
        mock_input.return_value = ""
        result = self.interactions.confirm("Test message")
        assert result.is_success
        assert result.value is False

    @patch('builtins.input')
    def test_confirm_default_true(self, mock_input: MagicMock) -> None:
        """Test confirm with default True."""
        mock_input.return_value = ""
        result = self.interactions.confirm("Test message", default=True)
        assert result.is_success
        assert result.value is True

    @patch('builtins.input')
    def test_confirm_yes_response(self, mock_input: MagicMock) -> None:
        """Test confirm with yes response."""
        mock_input.return_value = "y"
        result = self.interactions.confirm("Test message")
        assert result.is_success
        assert result.value is True

    @patch('builtins.input')
    def test_confirm_yes_upper_response(self, mock_input: MagicMock) -> None:
        """Test confirm with YES response."""
        mock_input.return_value = "YES"
        result = self.interactions.confirm("Test message")
        assert result.is_success
        assert result.value is True

    @patch('builtins.input')
    def test_confirm_no_response(self, mock_input: MagicMock) -> None:
        """Test confirm with no response."""
        mock_input.return_value = "n"
        result = self.interactions.confirm("Test message")
        assert result.is_success
        assert result.value is False

    @patch('builtins.input')
    def test_confirm_invalid_response(self, mock_input: MagicMock) -> None:
        """Test confirm with invalid response."""
        mock_input.return_value = "maybe"
        result = self.interactions.confirm("Test message")
        assert result.is_success
        assert result.value is False  # default

    @patch('builtins.input')
    def test_confirm_keyboard_interrupt(self, mock_input: MagicMock) -> None:
        """Test confirm with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        result = self.interactions.confirm("Test message")
        assert result.is_failure
        assert "User interrupted" in result.error

    @patch('builtins.input')
    def test_confirm_eof_error(self, mock_input: MagicMock) -> None:
        """Test confirm with EOF error."""
        mock_input.side_effect = EOFError()
        result = self.interactions.confirm("Test message")
        assert result.is_failure
        assert "Input stream ended" in result.error

    @patch('builtins.input')
    def test_confirm_quiet_mode(self, mock_input: MagicMock) -> None:
        """Test confirm in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.confirm("Test message", default=True)
        assert result.is_success
        assert result.value is True
        mock_input.assert_not_called()

    @patch('builtins.input')
    def test_prompt_with_default(self, mock_input: MagicMock) -> None:
        """Test prompt with default value."""
        mock_input.return_value = ""
        result = self.interactions.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.value == "default_value"

    @patch('builtins.input')
    def test_prompt_with_input(self, mock_input: MagicMock) -> None:
        """Test prompt with user input."""
        mock_input.return_value = "user_input"
        result = self.interactions.prompt("Test message")
        assert result.is_success
        assert result.value == "user_input"

    @patch('builtins.input')
    def test_prompt_empty_input_no_default(self, mock_input: MagicMock) -> None:
        """Test prompt with empty input and no default."""
        mock_input.return_value = ""
        result = self.interactions.prompt("Test message")
        assert result.is_failure
        assert "Empty input is not allowed" in result.error

    @patch('builtins.input')
    def test_prompt_keyboard_interrupt(self, mock_input: MagicMock) -> None:
        """Test prompt with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        result = self.interactions.prompt("Test message")
        assert result.is_failure
        assert "User interrupted" in result.error

    @patch('builtins.input')
    def test_prompt_eof_error(self, mock_input: MagicMock) -> None:
        """Test prompt with EOF error."""
        mock_input.side_effect = EOFError()
        result = self.interactions.prompt("Test message")
        assert result.is_failure
        assert "Input stream ended" in result.error

    @patch('builtins.input')
    def test_prompt_quiet_mode(self, mock_input: MagicMock) -> None:
        """Test prompt in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.value == "default_value"
        mock_input.assert_not_called()

    def test_print_status_info(self) -> None:
        """Test print status info."""
        result = self.interactions.print_status("Test info message", status="info")
        assert result.is_success

    def test_print_status_success(self) -> None:
        """Test print status success."""
        result = self.interactions.print_status("Test success message", status="success")
        assert result.is_success

    def test_print_status_warning(self) -> None:
        """Test print status warning."""
        result = self.interactions.print_status("Test warning message", status="warning")
        assert result.is_success

    def test_print_status_error(self) -> None:
        """Test print status error."""
        result = self.interactions.print_status("Test error message", status="error")
        assert result.is_success

    def test_print_status_unknown(self) -> None:
        """Test print status with unknown status."""
        result = self.interactions.print_status("Test message", status="unknown")
        assert result.is_success

    def test_print_status_quiet_mode(self) -> None:
        """Test print status in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.print_status("Test message", status="info")
        assert result.is_success

    def test_print_success(self) -> None:
        """Test print success."""
        result = self.interactions.print_success("Test success message")
        assert result.is_success

    def test_print_error(self) -> None:
        """Test print error."""
        result = self.interactions.print_error("Test error message")
        assert result.is_success

    def test_print_warning(self) -> None:
        """Test print warning."""
        result = self.interactions.print_warning("Test warning message")
        assert result.is_success

    def test_print_info(self) -> None:
        """Test print info."""
        result = self.interactions.print_info("Test info message")
        assert result.is_success

    def test_create_progress(self) -> None:
        """Test create progress."""
        result = self.interactions.create_progress("Test progress message")
        assert result.is_success
        assert result.value == "Test progress message"

    def test_create_progress_empty_message(self) -> None:
        """Test create progress with empty message."""
        result = self.interactions.create_progress("")
        assert result.is_success
        assert result.value == ""

    def test_create_progress_quiet_mode(self) -> None:
        """Test create progress in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.create_progress("Test progress message")
        assert result.is_success
        assert result.value == "Test progress message"

    def test_with_progress(self) -> None:
        """Test with progress."""
        items = [1, 2, 3, 4, 5]
        result = self.interactions.with_progress(items, "Test progress message")
        assert result.is_success
        assert result.value == items

    def test_with_progress_empty_items(self) -> None:
        """Test with progress with empty items."""
        items = []
        result = self.interactions.with_progress(items, "Test progress message")
        assert result.is_success
        assert result.value == items

    def test_with_progress_quiet_mode(self) -> None:
        """Test with progress in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        items = [1, 2, 3]
        result = interactions.with_progress(items, "Test progress message")
        assert result.is_success
        assert result.value == items
