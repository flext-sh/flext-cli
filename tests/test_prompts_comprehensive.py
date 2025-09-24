"""Comprehensive tests for FlextCliPrompts to achieve 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from flext_cli.prompts import FlextCliPrompts
from flext_core import FlextLogger


class TestFlextCliPrompts:
    """Comprehensive test suite for FlextCliPrompts."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        prompts = FlextCliPrompts()
        assert isinstance(prompts._logger, FlextLogger)
        assert prompts._quiet is False

    def test_init_with_logger(self) -> None:
        """Test initialization with custom logger."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        assert prompts._logger is logger
        assert prompts._quiet is False

    def test_init_quiet_mode(self) -> None:
        """Test initialization in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        assert prompts._quiet is True

    def test_execute(self) -> None:
        """Test execute method."""
        prompts = FlextCliPrompts()
        result = prompts.execute()
        assert result.is_success
        assert result.data is None

    def test_confirm_quiet_mode_default_true(self) -> None:
        """Test confirm in quiet mode with default True."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.confirm("Test message", default=True)
        assert result.is_success
        assert result.data is True

    def test_confirm_quiet_mode_default_false(self) -> None:
        """Test confirm in quiet mode with default False."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.confirm("Test message", default=False)
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_user_input_yes(self, mock_input: Mock) -> None:
        """Test confirm with user input 'yes'."""
        mock_input.return_value = "yes"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_user_input_y(self, mock_input: Mock) -> None:
        """Test confirm with user input 'y'."""
        mock_input.return_value = "y"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_user_input_1(self, mock_input: Mock) -> None:
        """Test confirm with user input '1'."""
        mock_input.return_value = "1"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_user_input_true(self, mock_input: Mock) -> None:
        """Test confirm with user input 'true'."""
        mock_input.return_value = "true"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_user_input_no(self, mock_input: Mock) -> None:
        """Test confirm with user input 'no'."""
        mock_input.return_value = "no"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_user_input_n(self, mock_input: Mock) -> None:
        """Test confirm with user input 'n'."""
        mock_input.return_value = "n"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_user_input_0(self, mock_input: Mock) -> None:
        """Test confirm with user input '0'."""
        mock_input.return_value = "0"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_user_input_false(self, mock_input: Mock) -> None:
        """Test confirm with user input 'false'."""
        mock_input.return_value = "false"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_user_input_empty_default_false(self, mock_input: Mock) -> None:
        """Test confirm with empty input and default False."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=False)
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_user_input_empty_default_true(self, mock_input: Mock) -> None:
        """Test confirm with empty input and default True."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=True)
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_user_input_invalid(self, mock_input: Mock) -> None:
        """Test confirm with invalid input."""
        mock_input.return_value = "invalid"
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "warning") as mock_warning:
            result = prompts.confirm("Test message", default=False)
            assert result.is_success
            assert result.data is False
            mock_warning.assert_called_once()

    @patch("builtins.input")
    def test_confirm_keyboard_interrupt(self, mock_input: Mock) -> None:
        """Test confirm with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_failure
        assert "User interrupted confirmation" in result.error

    @patch("builtins.input")
    def test_confirm_eof_error(self, mock_input: Mock) -> None:
        """Test confirm with EOF error."""
        mock_input.side_effect = EOFError()
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_failure
        assert "Input stream ended" in result.error

    @patch("builtins.input")
    def test_confirm_general_exception(self, mock_input: Mock) -> None:
        """Test confirm with general exception."""
        mock_input.side_effect = Exception("Test error")
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_failure
        assert "Confirmation failed: Test error" in result.error

    def test_prompt_quiet_mode_with_default(self) -> None:
        """Test prompt in quiet mode with default value."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.data == "default_value"

    def test_prompt_quiet_mode_no_default(self) -> None:
        """Test prompt in quiet mode without default value."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert "Empty input is not allowed" in result.error

    @patch("builtins.input")
    def test_prompt_user_input_valid(self, mock_input: Mock) -> None:
        """Test prompt with valid user input."""
        mock_input.return_value = "user_input"
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_success
        assert result.data == "user_input"

    @patch("builtins.input")
    def test_prompt_user_input_empty_with_default(self, mock_input: Mock) -> None:
        """Test prompt with empty input and default value."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.data == "default_value"

    @patch("builtins.input")
    def test_prompt_user_input_empty_no_default(self, mock_input: Mock) -> None:
        """Test prompt with empty input and no default."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert "Empty input is not allowed" in result.error

    @patch("builtins.input")
    def test_prompt_keyboard_interrupt(self, mock_input: Mock) -> None:
        """Test prompt with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert "User interrupted prompt" in result.error

    @patch("builtins.input")
    def test_prompt_eof_error(self, mock_input: Mock) -> None:
        """Test prompt with EOF error."""
        mock_input.side_effect = EOFError()
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert "Input stream ended" in result.error

    @patch("builtins.input")
    def test_prompt_general_exception(self, mock_input: Mock) -> None:
        """Test prompt with general exception."""
        mock_input.side_effect = Exception("Test error")
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert "Prompt failed: Test error" in result.error

    def test_print_status_info_quiet(self) -> None:
        """Test print_status with info level in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.print_status("Test message", status="info")
        assert result.is_success

    def test_print_status_info_not_quiet(self) -> None:
        """Test print_status with info level not in quiet mode."""
        prompts = FlextCliPrompts(quiet=False)
        with patch.object(prompts._logger, "info") as mock_info:
            result = prompts.print_status("Test message", status="info")
            assert result.is_success
            mock_info.assert_called_once_with("Test message")

    def test_print_status_success(self) -> None:
        """Test print_status with success level."""
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "info") as mock_info:
            result = prompts.print_status("Test message", status="success")
            assert result.is_success
            mock_info.assert_called_once_with("SUCCESS: Test message")

    def test_print_status_warning(self) -> None:
        """Test print_status with warning level."""
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "warning") as mock_warning:
            result = prompts.print_status("Test message", status="warning")
            assert result.is_success
            mock_warning.assert_called_once_with("Test message")

    def test_print_status_error(self) -> None:
        """Test print_status with error level."""
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "error") as mock_error:
            result = prompts.print_status("Test message", status="error")
            assert result.is_success
            mock_error.assert_called_once_with("Test message")

    def test_print_status_other(self) -> None:
        """Test print_status with other status level."""
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "info") as mock_info:
            result = prompts.print_status("Test message", status="custom")
            assert result.is_success
            mock_info.assert_called_once_with("CUSTOM: Test message")

    def test_print_status_exception(self) -> None:
        """Test print_status with exception."""
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "info", side_effect=Exception("Test error")):
            result = prompts.print_status("Test message", status="info")
            assert result.is_failure
            assert "Print status failed: Test error" in result.error

    def test_print_success(self) -> None:
        """Test print_success method."""
        prompts = FlextCliPrompts()
        result = prompts.print_success("Test message")
        assert result.is_success
        assert result.data is None

    def test_print_error(self) -> None:
        """Test print_error method."""
        prompts = FlextCliPrompts()
        result = prompts.print_error("Test message")
        assert result.is_success
        assert result.data is None

    def test_print_warning(self) -> None:
        """Test print_warning method."""
        prompts = FlextCliPrompts()
        result = prompts.print_warning("Test message")
        assert result.is_success
        assert result.data is None

    def test_print_info(self) -> None:
        """Test print_info method."""
        prompts = FlextCliPrompts()
        result = prompts.print_info("Test message")
        assert result.is_success
        assert result.data is None

    def test_create_progress_with_message_not_quiet(self) -> None:
        """Test create_progress with message not in quiet mode."""
        prompts = FlextCliPrompts(quiet=False)
        with patch.object(prompts._logger, "info") as mock_info:
            result = prompts.create_progress("Test progress")
            assert result.is_success
            assert result.data == "Test progress"
            mock_info.assert_called_once_with("Starting: Test progress")

    def test_create_progress_with_message_quiet(self) -> None:
        """Test create_progress with message in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.create_progress("Test progress")
        assert result.is_success
        assert result.data == "Test progress"

    def test_create_progress_empty_message(self) -> None:
        """Test create_progress with empty message."""
        prompts = FlextCliPrompts()
        result = prompts.create_progress("")
        assert result.is_success
        assert not result.data

    def test_create_progress_exception(self) -> None:
        """Test create_progress with exception."""
        prompts = FlextCliPrompts()
        with patch.object(prompts._logger, "info", side_effect=Exception("Test error")):
            result = prompts.create_progress("Test progress")
            assert result.is_failure
            assert "Progress creation failed: Test error" in result.error

    def test_with_progress_not_quiet(self) -> None:
        """Test with_progress not in quiet mode."""
        prompts = FlextCliPrompts(quiet=False)
        items = [1, 2, 3]
        with patch.object(prompts._logger, "info") as mock_info:
            result = prompts.with_progress(items, "Test progress")
            assert result.is_success
            assert result.data == items
            mock_info.assert_called_once_with("Processing 3 items: Test progress")

    def test_with_progress_quiet(self) -> None:
        """Test with_progress in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        items = [1, 2, 3]
        result = prompts.with_progress(items, "Test progress")
        assert result.is_success
        assert result.data == items

    def test_with_progress_empty_message(self) -> None:
        """Test with_progress with empty message."""
        prompts = FlextCliPrompts()
        items = [1, 2, 3]
        result = prompts.with_progress(items, "")
        assert result.is_success
        assert result.data == items

    def test_with_progress_exception(self) -> None:
        """Test with_progress with exception."""
        prompts = FlextCliPrompts()
        items = [1, 2, 3]
        with patch.object(prompts._logger, "info", side_effect=Exception("Test error")):
            result = prompts.with_progress(items, "Test progress")
            assert result.is_failure
            assert "Progress processing failed: Test error" in result.error


class TestFlextCliPromptsIntegration:
    """Integration tests for FlextCliPrompts."""

    def test_full_workflow(self) -> None:
        """Test complete workflow with multiple operations."""
        prompts = FlextCliPrompts(quiet=True)

        # Test execute
        result = prompts.execute()
        assert result.is_success

        # Test confirm
        result = prompts.confirm("Test", default=True)
        assert result.is_success
        assert result.data is True

        # Test prompt
        result = prompts.prompt("Test", default="default")
        assert result.is_success
        assert result.data == "default"

        # Test status printing
        result = prompts.print_success("Success message")
        assert result.is_success

        # Test progress
        result = prompts.create_progress("Progress message")
        assert result.is_success

        # Test with_progress
        items = ["item1", "item2"]
        result = prompts.with_progress(items, "Processing")
        assert result.is_success
        assert result.data == items

    def test_error_handling_chain(self) -> None:
        """Test error handling in method chains."""
        prompts = FlextCliPrompts()

        # Test that errors are properly propagated
        with patch("builtins.input", side_effect=KeyboardInterrupt()):
            result = prompts.confirm("Test")
            assert result.is_failure

        with patch("builtins.input", side_effect=EOFError()):
            result = prompts.prompt("Test")
            assert result.is_failure
