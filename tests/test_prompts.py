"""Tests for flext_cli.prompts module."""

from unittest.mock import MagicMock, patch

from flext_cli.prompts import FlextCliPrompts
from flext_core import FlextLogger


class TestFlextCliPrompts:
    """Test cases for FlextCliPrompts class."""

    def test_init_default(self) -> None:
        """Test initialization with default parameters."""
        prompts = FlextCliPrompts()
        assert prompts._quiet is False
        assert isinstance(prompts._logger, FlextLogger)

    def test_init_with_logger(self) -> None:
        """Test initialization with custom logger."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        assert prompts._logger is logger
        assert prompts._quiet is False

    def test_init_with_quiet(self) -> None:
        """Test initialization with quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        assert prompts._quiet is True

    def test_execute(self) -> None:
        """Test execute method."""
        prompts = FlextCliPrompts()
        result = prompts.execute()
        assert result.is_success
        assert result.value is None

    @patch("builtins.input")
    def test_confirm_default_false(self, mock_input: MagicMock) -> None:
        """Test confirm with default False."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")

        assert result.is_success
        assert result.value is False
        mock_input.assert_called_once_with("Test message [y/N]: ")

    @patch("builtins.input")
    def test_confirm_default_true(self, mock_input: MagicMock) -> None:
        """Test confirm with default True."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=True)

        assert result.is_success
        assert result.value is True
        mock_input.assert_called_once_with("Test message [Y/n]: ")

    @patch("builtins.input")
    def test_confirm_yes_responses(self, mock_input: MagicMock) -> None:
        """Test confirm with various yes responses."""
        prompts = FlextCliPrompts()

        for response in ["y", "yes", "1", "true"]:
            mock_input.return_value = response
            result = prompts.confirm("Test message")
            assert result.is_success
            assert result.value is True

    @patch("builtins.input")
    def test_confirm_no_responses(self, mock_input: MagicMock) -> None:
        """Test confirm with various no responses."""
        prompts = FlextCliPrompts()

        for response in ["n", "no", "0", "false"]:
            mock_input.return_value = response
            result = prompts.confirm("Test message")
            assert result.is_success
            assert result.value is False

    @patch("builtins.input")
    def test_confirm_invalid_response(self, mock_input: MagicMock) -> None:
        """Test confirm with invalid response."""
        mock_input.return_value = "maybe"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=True)

        assert result.is_success
        assert result.value is True  # Uses default

    @patch("builtins.input")
    def test_confirm_keyboard_interrupt(self, mock_input: MagicMock) -> None:
        """Test confirm with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")

        assert result.is_failure
        assert "User interrupted confirmation" in result.error

    @patch("builtins.input")
    def test_confirm_eof_error(self, mock_input: MagicMock) -> None:
        """Test confirm with EOF error."""
        mock_input.side_effect = EOFError()
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")

        assert result.is_failure
        assert "Input stream ended" in result.error

    @patch("builtins.input")
    def test_confirm_quiet_mode(self, mock_input: MagicMock) -> None:
        """Test confirm in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.confirm("Test message", default=True)

        assert result.is_success
        assert result.value is True
        mock_input.assert_not_called()

    @patch("builtins.input")
    def test_prompt_with_default(self, mock_input: MagicMock) -> None:
        """Test prompt with default value."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message", default="default_value")

        assert result.is_success
        assert result.value == "default_value"
        mock_input.assert_called_once_with("Test message [default_value]: ")

    @patch("builtins.input")
    def test_prompt_without_default(self, mock_input: MagicMock) -> None:
        """Test prompt without default value."""
        mock_input.return_value = "user_input"
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")

        assert result.is_success
        assert result.value == "user_input"
        mock_input.assert_called_once_with("Test message: ")

    @patch("builtins.input")
    def test_prompt_empty_input_no_default(self, mock_input: MagicMock) -> None:
        """Test prompt with empty input and no default."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")

        assert result.is_failure
        assert "Empty input is not allowed" in result.error

    @patch("builtins.input")
    def test_prompt_keyboard_interrupt(self, mock_input: MagicMock) -> None:
        """Test prompt with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")

        assert result.is_failure
        assert "User interrupted prompt" in result.error

    @patch("builtins.input")
    def test_prompt_eof_error(self, mock_input: MagicMock) -> None:
        """Test prompt with EOF error."""
        mock_input.side_effect = EOFError()
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")

        assert result.is_failure
        assert "Input stream ended" in result.error

    @patch("builtins.input")
    def test_prompt_quiet_mode_with_default(self, mock_input: MagicMock) -> None:
        """Test prompt in quiet mode with default."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.prompt("Test message", default="default_value")

        assert result.is_success
        assert result.value == "default_value"
        mock_input.assert_not_called()

    @patch("builtins.input")
    def test_prompt_quiet_mode_without_default(self, mock_input: MagicMock) -> None:
        """Test prompt in quiet mode without default."""
        mock_input.return_value = "user_input"
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.prompt("Test message")

        assert result.is_failure
        assert "Empty input is not allowed" in result.error
        mock_input.assert_not_called()

    @patch.object(FlextLogger, "info")
    def test_print_status_info(self, mock_logger_info: MagicMock) -> None:
        """Test print_status with info level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_status("Test message", status="info")

        assert result.is_success
        mock_logger_info.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "info")
    def test_print_status_success(self, mock_logger_info: MagicMock) -> None:
        """Test print_status with success level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_status("Test message", status="success")

        assert result.is_success
        mock_logger_info.assert_called_once_with("SUCCESS: Test message")

    @patch.object(FlextLogger, "warning")
    def test_print_status_warning(self, mock_logger_warning: MagicMock) -> None:
        """Test print_status with warning level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_status("Test message", status="warning")

        assert result.is_success
        mock_logger_warning.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "error")
    def test_print_status_error(self, mock_logger_error: MagicMock) -> None:
        """Test print_status with error level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_status("Test message", status="error")

        assert result.is_success
        mock_logger_error.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "info")
    def test_print_status_custom(self, mock_logger_info: MagicMock) -> None:
        """Test print_status with custom level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_status("Test message", status="custom")

        assert result.is_success
        mock_logger_info.assert_called_once_with("CUSTOM: Test message")

    @patch.object(FlextLogger, "info")
    def test_print_status_quiet_mode_info(self, mock_logger_info: MagicMock) -> None:
        """Test print_status in quiet mode with info level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger, quiet=True)
        result = prompts.print_status("Test message", status="info")

        assert result.is_success
        mock_logger_info.assert_not_called()

    @patch.object(FlextLogger, "warning")
    def test_print_status_quiet_mode_warning(
        self, mock_logger_warning: MagicMock
    ) -> None:
        """Test print_status in quiet mode with warning level."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger, quiet=True)
        result = prompts.print_status("Test message", status="warning")

        assert result.is_success
        mock_logger_warning.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "info")
    def test_print_success(self, mock_logger_info: MagicMock) -> None:
        """Test print_success method."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_success("Test message")

        assert result.is_success
        mock_logger_info.assert_called_once_with("SUCCESS: Test message")

    @patch.object(FlextLogger, "error")
    def test_print_error(self, mock_logger_error: MagicMock) -> None:
        """Test print_error method."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_error("Test message")

        assert result.is_success
        mock_logger_error.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "warning")
    def test_print_warning(self, mock_logger_warning: MagicMock) -> None:
        """Test print_warning method."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_warning("Test message")

        assert result.is_success
        mock_logger_warning.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "info")
    def test_print_info(self, mock_logger_info: MagicMock) -> None:
        """Test print_info method."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_info("Test message")

        assert result.is_success
        mock_logger_info.assert_called_once_with("Test message")

    @patch.object(FlextLogger, "info")
    def test_create_progress_with_message(self, mock_logger_info: MagicMock) -> None:
        """Test create_progress with message."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.create_progress("Test progress")

        assert result.is_success
        assert result.value == "Test progress"
        mock_logger_info.assert_called_once_with("Starting: Test progress")

    @patch.object(FlextLogger, "info")
    def test_create_progress_empty_message(self, mock_logger_info: MagicMock) -> None:
        """Test create_progress with empty message."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.create_progress("")

        assert result.is_success
        assert not result.value
        mock_logger_info.assert_not_called()

    @patch.object(FlextLogger, "info")
    def test_create_progress_quiet_mode(self, mock_logger_info: MagicMock) -> None:
        """Test create_progress in quiet mode."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger, quiet=True)
        result = prompts.create_progress("Test progress")

        assert result.is_success
        assert result.value == "Test progress"
        mock_logger_info.assert_not_called()

    @patch.object(FlextLogger, "info")
    def test_with_progress_with_message(self, mock_logger_info: MagicMock) -> None:
        """Test with_progress with message."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        items = [1, 2, 3]
        result = prompts.with_progress(items, "Processing items")

        assert result.is_success
        assert result.value == items
        mock_logger_info.assert_called_once_with("Processing 3 items: Processing items")

    @patch.object(FlextLogger, "info")
    def test_with_progress_empty_message(self, mock_logger_info: MagicMock) -> None:
        """Test with_progress with empty message."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        items = [1, 2, 3]
        result = prompts.with_progress(items, "")

        assert result.is_success
        assert result.value == items
        mock_logger_info.assert_not_called()

    @patch.object(FlextLogger, "info")
    def test_with_progress_quiet_mode(self, mock_logger_info: MagicMock) -> None:
        """Test with_progress in quiet mode."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger, quiet=True)
        items = [1, 2, 3]
        result = prompts.with_progress(items, "Processing items")

        assert result.is_success
        assert result.value == items
        mock_logger_info.assert_not_called()

    @patch.object(FlextLogger, "info")
    def test_print_status_exception(self, mock_logger_info: MagicMock) -> None:
        """Test print_status with exception."""
        mock_logger_info.side_effect = Exception("Logger error")
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.print_status("Test message", status="info")

        assert result.is_failure
        assert "Print status failed" in result.error

    @patch.object(FlextLogger, "info")
    def test_create_progress_exception(self, mock_logger_info: MagicMock) -> None:
        """Test create_progress with exception."""
        mock_logger_info.side_effect = Exception("Logger error")
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        result = prompts.create_progress("Test progress")

        assert result.is_failure
        assert "Progress creation failed" in result.error

    @patch.object(FlextLogger, "info")
    def test_with_progress_exception(self, mock_logger_info: MagicMock) -> None:
        """Test with_progress with exception."""
        mock_logger_info.side_effect = Exception("Logger error")
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        items = [1, 2, 3]
        result = prompts.with_progress(items, "Processing items")

        assert result.is_failure
        assert "Progress processing failed" in result.error
