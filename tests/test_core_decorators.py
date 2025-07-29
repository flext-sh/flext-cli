"""Tests for core decorators in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from flext_cli.core.decorators import (
    async_command,
    confirm_action,
    measure_time,
    require_auth,
    retry,
    validate_config,
    with_spinner,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3

if TYPE_CHECKING:
    from pathlib import Path


class TestAsyncCommand:
    """Test cases for async_command decorator."""

    def test_async_command_decorator(self) -> None:
        """Test async command decorator."""

        @async_command
        async def sample_async_function() -> str:
            await asyncio.sleep(0.01)
            return "async result"

        # Decorator converts async to sync, so it should NOT be a coroutine function
        assert not asyncio.iscoroutinefunction(sample_async_function)

        # Test execution (now sync)
        result = sample_async_function()
        if result != "async result":
            msg = f"Expected {'async result'}, got {result}"
            raise AssertionError(msg)

    def test_async_command_with_arguments(self) -> None:
        """Test async command decorator with arguments."""

        @async_command
        async def async_function_with_args(arg1: str, arg2: int) -> str:
            await asyncio.sleep(0.01)
            return f"{arg1}-{arg2}"

        # Decorator converts async to sync
        result = async_function_with_args("test", 42)
        if result != "test-42":
            msg = f"Expected {'test-42'}, got {result}"
            raise AssertionError(msg)

    def test_async_command_preserves_metadata(self) -> None:
        """Test that async command decorator preserves function metadata."""

        @async_command
        async def documented_async_function() -> str:
            """A documented async function."""
            return "result"

        if documented_async_function.__name__ != "documented_async_function":
            msg = f"Expected {'documented_async_function'}, got {documented_async_function.__name__}"
            raise AssertionError(msg)
        assert documented_async_function.__doc__ == "A documented async function."


class TestConfirmAction:
    """Test cases for confirm_action decorator."""

    @patch("rich.console.Console.input")
    def test_confirm_action_confirmed(self, mock_input: Mock) -> None:
        """Test confirm action when user confirms."""
        mock_input.return_value = "y"

        @confirm_action("Are you sure?")
        def dangerous_action() -> str:
            return "action executed"

        result = dangerous_action()
        if result != "action executed":
            msg = f"Expected {'action executed'}, got {result}"
            raise AssertionError(msg)

    @patch("rich.console.Console.input")
    def test_confirm_action_cancelled(self, mock_input: Mock) -> None:
        """Test confirm action when user cancels."""
        mock_input.return_value = "n"

        @confirm_action("Are you sure?")
        def dangerous_action() -> str:
            return "action executed"

        result = dangerous_action()
        assert result is None  # Should return None when cancelled

    @patch("rich.console.Console.input")
    def test_confirm_action_with_custom_message(self, mock_input: Mock) -> None:
        """Test confirm action with custom message."""
        mock_input.return_value = "yes"

        @confirm_action("Delete all files?")
        def delete_files() -> str:
            return "files deleted"

        result = delete_files()
        if result != "files deleted":
            msg = f"Expected {'files deleted'}, got {result}"
            raise AssertionError(msg)

    @patch("rich.console.Console.input")
    def test_confirm_action_with_arguments(self, mock_input: Mock) -> None:
        """Test confirm action with function arguments."""
        mock_input.return_value = "y"

        @confirm_action("Proceed with action?")
        def action_with_args(name: str, count: int) -> str:
            return f"processed {count} items for {name}"

        result = action_with_args("test", 5)
        if result != "processed 5 items for test":
            msg = f"Expected {'processed 5 items for test'}, got {result}"
            raise AssertionError(msg)


class TestRequireAuth:
    """Test cases for require_auth decorator."""

    def test_require_auth_with_existing_token(self, temp_dir: Path) -> None:
        """Test require_auth when token file exists."""
        token_file = temp_dir / "token"
        token_file.write_text("valid-token-123")

        @require_auth(token_file=str(token_file))
        def protected_function(auth_token: str) -> str:
            return "access granted"

        result = protected_function()
        if result != "access granted":
            msg = f"Expected {'access granted'}, got {result}"
            raise AssertionError(msg)

    def test_require_auth_missing_token_file(self, temp_dir: Path) -> None:
        """Test require_auth when token file doesn't exist."""
        token_file = temp_dir / "nonexistent_token"

        @require_auth(token_file=str(token_file))
        def protected_function() -> str:
            return "access granted"

        result = protected_function()
        assert result is None  # Should return None when auth fails

    def test_require_auth_empty_token_file(self, temp_dir: Path) -> None:
        """Test require_auth when token file is empty."""
        token_file = temp_dir / "empty_token"
        token_file.write_text("")

        @require_auth(token_file=str(token_file))
        def protected_function() -> str:
            return "access granted"

        result = protected_function()
        assert result is None  # Should return None when token is empty

    def test_require_auth_with_default_path(self) -> None:
        """Test require_auth with default token path."""

        @require_auth()
        def protected_function() -> str:
            return "access granted"

        # Should not raise if using default behavior
        # (This test verifies the decorator can be applied without errors)
        assert callable(protected_function)


class TestMeasureTime:
    """Test cases for measure_time decorator."""

    @patch("flext_cli.core.decorators.time.time")
    @patch("rich.console.Console.print")
    def test_measure_time_with_output(self, mock_print: Mock, mock_time: Mock) -> None:
        """Test measure_time decorator with output enabled."""
        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 seconds elapsed

        @measure_time(show_in_output=True)
        def timed_function() -> str:
            return "completed"

        result = timed_function()

        if result != "completed":
            msg = f"Expected {'completed'}, got {result}"
            raise AssertionError(msg)
        mock_print.assert_called_once_with("⏱️  Execution time: 2.50s", style="dim")

    @patch("flext_cli.core.decorators.time.time")
    @patch("rich.console.Console.print")
    def test_measure_time_without_output(
        self,
        mock_print: Mock,
        mock_time: Mock,
    ) -> None:
        """Test measure_time decorator with output disabled."""
        mock_time.side_effect = [1000.0, 1001.0]  # 1 second elapsed

        @measure_time(show_in_output=False)
        def timed_function() -> str:
            return "completed"

        result = timed_function()

        if result != "completed":
            msg = f"Expected {'completed'}, got {result}"
            raise AssertionError(msg)
        mock_print.assert_not_called()

    @patch("flext_cli.core.decorators.time.time")
    def test_measure_time_preserves_function_signature(self, mock_time: Mock) -> None:
        """Test that measure_time preserves function signature."""
        mock_time.side_effect = [1000.0, 1001.0]

        @measure_time()
        def function_with_args(arg1: str, arg2: int, kwarg1: str = "default") -> str:
            return f"{arg1}-{arg2}-{kwarg1}"

        result = function_with_args("test", 42, kwarg1="custom")
        if result != "test-42-custom":
            msg = f"Expected {'test-42-custom'}, got {result}"
            raise AssertionError(msg)


class TestRetry:
    """Test cases for retry decorator."""

    def test_retry_success_on_first_attempt(self) -> None:
        """Test retry when function succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def reliable_function() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = reliable_function()
        if result != "success":
            msg = f"Expected {'success'}, got {result}"
            raise AssertionError(msg)
        assert call_count == 1

    def test_retry_success_after_failures(self) -> None:
        """Test retry when function succeeds after some failures."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def flaky_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "temporary error"
                raise ValueError(msg)
            return "success"

        result = flaky_function()
        if result != "success":
            msg = f"Expected {'success'}, got {result}"
            raise AssertionError(msg)
        assert call_count == EXPECTED_DATA_COUNT

    def test_retry_max_attempts_exceeded(self) -> None:
        """Test retry when max attempts are exceeded."""
        call_count = 0

        @retry(max_attempts=2, delay=0.01)
        def failing_function() -> str:
            nonlocal call_count
            call_count += 1
            msg = "persistent error"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="persistent error"):
            failing_function()

        if call_count != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {call_count}"
            raise AssertionError(msg)

    @patch("flext_cli.core.decorators.time.sleep")
    def test_retry_delay_between_attempts(self, mock_sleep: Mock) -> None:
        """Test retry delay between attempts."""
        call_count = 0

        @retry(max_attempts=3, delay=0.5)
        def flaky_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                msg = "error"
                raise ValueError(msg)
            return "success"

        result = flaky_function()
        if result != "success":
            msg = f"Expected {'success'}, got {result}"
            raise AssertionError(msg)
        mock_sleep.assert_called_once_with(0.5)


class TestValidateConfig:
    """Test cases for validate_config decorator."""

    def test_validate_config_with_valid_config(self) -> None:
        """Test validate_config with valid configuration."""

        # Create mock config object with required attributes
        class MockConfig:
            api_url = "http://localhost:8000"
            timeout = 30

        @validate_config(["api_url", "timeout"])
        def function_requiring_config(config: MockConfig) -> str:
            return "config validated"

        result = function_requiring_config(config=MockConfig())
        if result != "config validated":
            msg = f"Expected {'config validated'}, got {result}"
            raise AssertionError(msg)

    @patch("rich.console.Console.print")
    def test_validate_config_with_missing_keys(self, mock_print: Mock) -> None:
        """Test validate_config with missing required keys."""

        # Create mock config object missing required attributes
        class MockConfig:
            api_url = "http://localhost:8000"
            # missing timeout

        @validate_config(["api_url", "timeout"])
        def function_requiring_config(config: MockConfig) -> str:
            return "config validated"

        result = function_requiring_config(config=MockConfig())
        assert result is None
        mock_print.assert_called_once_with(
            "Missing required configuration: timeout",
            style="red",
        )

    @patch("rich.console.Console.print")
    def test_validate_config_no_context(self, mock_print: Mock) -> None:
        """Test validate_config when no config available."""

        @validate_config(["api_url"])
        def function_requiring_config() -> str:
            return "config validated"

        result = function_requiring_config()  # No config provided
        assert result is None
        mock_print.assert_called_once_with(
            "Configuration not available for validation.",
            style="red",
        )


class TestWithSpinner:
    """Test cases for with_spinner decorator."""

    @patch("rich.console.Console.status")
    def test_with_spinner_default_message(self, mock_status: Mock) -> None:
        """Test with_spinner decorator with default message."""
        mock_context = Mock()
        mock_status.return_value.__enter__ = Mock(return_value=mock_context)
        mock_status.return_value.__exit__ = Mock(return_value=None)

        @with_spinner()
        def long_running_task() -> str:
            time.sleep(0.01)  # Simulate work
            return "task completed"

        result = long_running_task()
        if result != "task completed":
            msg = f"Expected {'task completed'}, got {result}"
            raise AssertionError(msg)
        mock_status.assert_called_once_with("Processing...", spinner="dots")

    @patch("rich.console.Console.status")
    def test_with_spinner_custom_message(self, mock_status: Mock) -> None:
        """Test with_spinner decorator with custom message."""
        mock_context = Mock()
        mock_status.return_value.__enter__ = Mock(return_value=mock_context)
        mock_status.return_value.__exit__ = Mock(return_value=None)

        @with_spinner("Calculating results...")
        def calculation_task() -> str:
            time.sleep(0.01)
            return "calculation done"

        result = calculation_task()
        if result != "calculation done":
            msg = f"Expected {'calculation done'}, got {result}"
            raise AssertionError(msg)
        mock_status.assert_called_once_with("Calculating results...", spinner="dots")

    @patch("rich.console.Console.status")
    def test_with_spinner_exception_handling(self, mock_status: Mock) -> None:
        """Test with_spinner decorator with exception handling."""
        mock_context = Mock()
        mock_status.return_value.__enter__ = Mock(return_value=mock_context)
        mock_status.return_value.__exit__ = Mock(return_value=None)

        @with_spinner("Processing...")
        def failing_task() -> str:
            msg = "task failed"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="task failed"):
            failing_task()

        mock_status.assert_called_once_with("Processing...", spinner="dots")


class TestDecoratorCombinations:
    """Test combinations of decorators."""

    @patch("rich.console.Console.input")
    @patch("flext_cli.core.decorators.time.time")
    def test_multiple_decorators(self, mock_time: Mock, mock_input: Mock) -> None:
        """Test combining multiple decorators."""
        mock_input.return_value = "y"
        mock_time.side_effect = [1000.0, 1001.0]

        @confirm_action("Proceed?")
        @measure_time(show_in_output=False)
        @retry(max_attempts=2, delay=0.01)
        def complex_function() -> str:
            return "all decorators applied"

        result = complex_function()
        if result != "all decorators applied":
            msg = f"Expected {'all decorators applied'}, got {result}"
            raise AssertionError(msg)

    def test_decorator_order_preservation(self) -> None:
        """Test that decorator order is preserved."""

        @measure_time(show_in_output=False)
        @retry(max_attempts=1, delay=0)
        def decorated_function() -> str:
            """A decorated function."""
            return "result"

        # Function should still be callable and maintain behavior
        assert callable(decorated_function)
        if decorated_function() != "result":
            msg = f"Expected {'result'}, got {decorated_function()}"
            raise AssertionError(msg)
        assert decorated_function.__doc__ == "A decorated function."
