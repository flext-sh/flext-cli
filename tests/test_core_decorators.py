"""Tests for core decorators in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from flext_core import FlextConstants

from flext_cli.decorators import FlextCliDecorators as D

# Map class methods to local names for decorator usage in tests
async_command = D.async_command
confirm_action = D.confirm_action
measure_time = D.measure_time
require_auth = D.require_auth
retry = D.retry
validate_config = D.validate_config
with_spinner = D.with_spinner

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestAsyncCommand:
    """Test cases for async_command decorator."""

    def test_async_command_decorator(self) -> None:
        """Test async command decorator."""

        @async_command
        async def sample_async_function() -> str:
            await asyncio.sleep(0.01)
            return "async result"

        # Decorator returns object type - test directly without type narrowing
        assert callable(sample_async_function)
        # Decorator converts async to sync, so it should NOT be a coroutine function
        assert not asyncio.iscoroutinefunction(sample_async_function)
        # Test execution (now sync)
        result = sample_async_function()

        if not isinstance(result, str) or result != "async result":
            msg: str = f"Expected {'async result'}, got {result}"
            raise AssertionError(msg)

    def test_async_command_with_arguments(self) -> None:
        """Test async command decorator with arguments."""

        @async_command
        async def async_function_with_args(arg1: str, arg2: int) -> str:
            await asyncio.sleep(0.01)
            return f"{arg1}-{arg2}"

        # Decorator returns object type - test directly without type narrowing
        assert callable(async_function_with_args)
        # Decorator converts async to sync
        result = async_function_with_args("test", 42)

        if not isinstance(result, str) or result != "test-42":
            msg: str = f"Expected {'test-42'}, got {result}"
            raise AssertionError(msg)

    def test_async_command_preserves_metadata(self) -> None:
        """Test that async command decorator preserves function metadata."""

        @async_command
        async def documented_async_function() -> str:
            """A documented async function."""
            return "result"

        # Decorator returns object type - test directly without type narrowing
        assert callable(documented_async_function)
        if (
            hasattr(documented_async_function, "__name__")
            and documented_async_function.__name__ != "documented_async_function"
        ):
            msg: str = f"Expected {'documented_async_function'}, got {documented_async_function.__name__}"
            raise AssertionError(msg)
        if hasattr(documented_async_function, "__doc__"):
            assert documented_async_function.__doc__ == "A documented async function."


class TestConfirmAction:
    """Test cases for confirm_action decorator."""

    def test_confirm_action_confirmed(self) -> None:
        """Test confirm action when user confirms."""
        with patch("rich.console.Console.input") as mock_input:
            mock_input.return_value = "y"

            # Test the decorator function directly without nested decorator usage
            def dangerous_action() -> str:
                return "action executed"

            # Apply decorator manually to avoid typing issues
            decorated_func = confirm_action("Are you sure?")(dangerous_action)
            assert callable(decorated_func)
            result = decorated_func()
            if result != "action executed":
                msg: str = f"Expected {'action executed'}, got {result}"
                raise AssertionError(msg)

    def test_confirm_action_cancelled(self) -> None:
        """Test confirm action when user cancels."""
        with patch("rich.console.Console.input") as mock_input:
            mock_input.return_value = "n"

            def dangerous_action() -> str:
                return "action executed"

            decorated_func = confirm_action("Are you sure?")(dangerous_action)
            assert callable(decorated_func)
            result = decorated_func()
            assert result is None  # Should return None when cancelled

    def test_confirm_action_with_custom_message(self) -> None:
        """Test confirm action with custom message."""
        with patch("rich.console.Console.input") as mock_input:
            mock_input.return_value = "yes"

            def delete_files() -> str:
                return "files deleted"

            decorated_func = confirm_action("Delete all files?")(delete_files)
            assert callable(decorated_func)
            result = decorated_func()
            if result != "files deleted":
                msg: str = f"Expected {'files deleted'}, got {result}"
                raise AssertionError(msg)

    def test_confirm_action_with_arguments(self) -> None:
        """Test confirm action with function arguments."""
        with patch("rich.console.Console.input") as mock_input:
            mock_input.return_value = "y"

            def action_with_args(name: str, count: int) -> str:
                return f"processed {count} items for {name}"

            decorated_func = confirm_action("Proceed with action?")(action_with_args)
            assert callable(decorated_func)
            result = decorated_func("test", 5)
            if result != "processed 5 items for test":
                msg: str = f"Expected {'processed 5 items for test'}, got {result}"
                raise AssertionError(msg)


class TestRequireAuth:
    """Test cases for require_auth decorator."""

    def test_require_auth_with_existing_token(self, temp_dir: Path) -> None:
        """Test require_auth when token file exists."""
        token_file = temp_dir / "token"
        token_file.write_text("valid-token-123")

        def protected_function() -> str:
            return "access granted"

        decorated_func = require_auth(token_file=str(token_file))(protected_function)
        assert callable(decorated_func)
        result = decorated_func()
        if result != "access granted":
            msg: str = f"Expected {'access granted'}, got {result}"
            raise AssertionError(msg)

    def test_require_auth_missing_token_file(self, temp_dir: Path) -> None:
        """Test require_auth when token file doesn't exist."""
        token_file = temp_dir / "nonexistent_token"

        def protected_function() -> str:
            return "access granted"

        decorated_func = require_auth(token_file=str(token_file))(protected_function)
        assert callable(decorated_func)
        result = decorated_func()
        assert result is None  # Should return None when auth fails

    def test_require_auth_empty_token_file(self, temp_dir: Path) -> None:
        """Test require_auth when token file is empty."""
        token_file = temp_dir / "empty_token"
        token_file.write_text("")

        def protected_function() -> str:
            return "access granted"

        decorated_func = require_auth(token_file=str(token_file))(protected_function)
        assert callable(decorated_func)
        result = decorated_func()
        assert result is None  # Should return None when token is empty

    def test_require_auth_with_default_path(self) -> None:
        """Test require_auth with default token path."""

        def protected_function() -> str:
            return "access granted"

        decorated_func = require_auth()(protected_function)
        # Should not raise if using default behavior
        # (This test verifies the decorator can be applied without errors)
        assert callable(decorated_func)


class TestMeasureTime:
    """Test cases for measure_time decorator."""

    def test_measure_time_with_output(self) -> None:
        """Test measure_time decorator with output enabled."""
        with (
            patch("flext_cli.decorators.time.time") as mock_time,
            patch("rich.console.Console.print") as mock_print,
        ):
            mock_time.side_effect = [1000.0, 1002.5]  # Start and end time

            @measure_time(show_in_output=True)
            def timed_function() -> str:
                return "completed"

            result = timed_function()
            if result != "completed":
                msg: str = f"Expected {'completed'}, got {result}"
                raise AssertionError(msg)
            mock_print.assert_called_once_with("⏱  Execution time: 2.50s", style="dim")

    def test_measure_time_without_output(self) -> None:
        """Test measure_time decorator with output disabled."""
        with (
            patch("flext_cli.decorators.time.time") as mock_time,
            patch("flext_cli.decorators.FlextLogger.info") as mock_logger,
        ):
            mock_time.side_effect = [1000.0, 1001.0]  # Start and end time

            @measure_time(show_in_output=False)
            def timed_function() -> str:
                return "completed"

            result = timed_function()
            if result != "completed":
                msg: str = f"Expected {'completed'}, got {result}"
                raise AssertionError(msg)
            mock_logger.assert_not_called()

    def test_measure_time_preserves_function_signature(self) -> None:
        """Test that measure_time preserves function signature."""
        with patch("flext_cli.decorators.time.time") as mock_time:
            mock_time.side_effect = [1000.0, 1001.0, 1002.0]

            @measure_time()
            def function_with_args(
                arg1: str,
                arg2: int,
                kwarg1: str = "default",
            ) -> str:
                return f"{arg1}-{arg2}-{kwarg1}"

            result = function_with_args("test", 42, kwarg1="custom")
            if result != "test-42-custom":
                msg: str = f"Expected {'test-42-custom'}, got {result}"
                raise AssertionError(msg)


class TestRetry:
    """Test cases for retry decorator."""

    def test_retry_success_on_first_attempt(self) -> None:
        """Test retry when function succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3)
        def reliable_function() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = reliable_function()
        if result != "success":
            msg: str = f"Expected {'success'}, got {result}"
            raise AssertionError(msg)
        assert call_count == 1

    def test_retry_success_after_failures(self) -> None:
        """Test retry when function succeeds after some failures."""
        call_count = 0

        @retry(max_attempts=3)
        def flaky_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "temporary error"
                raise ValueError(msg)
            return "success"

        result = flaky_function()
        if result != "success":
            msg: str = f"Expected {'success'}, got {result}"
            raise AssertionError(msg)
        assert call_count == EXPECTED_DATA_COUNT

    def test_retry_max_attempts_exceeded(self) -> None:
        """Test retry when max attempts are exceeded."""
        call_count = 0

        @retry(max_attempts=2)
        def failing_function() -> str:
            nonlocal call_count
            call_count += 1
            msg = "persistent error"
            raise ValueError(msg)

        # Retry decorator re-raises exception after exhausting attempts
        with pytest.raises(ValueError, match="persistent error"):
            failing_function()
        if call_count != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {call_count}"
            raise AssertionError(msg)

    def test_retry_delay_between_attempts(self) -> None:
        """Test retry delay between attempts."""
        with patch("flext_cli.decorators.time.sleep") as mock_sleep:
            call_count = 0

            @retry(max_attempts=3)
            def flaky_function() -> str:
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    msg = "error"
                    raise ValueError(msg)
                return "success"

            result = flaky_function()
            if result != "success":
                msg: str = f"Expected {'success'}, got {result}"
                raise AssertionError(msg)
            mock_sleep.assert_called_once_with(0.5)


class TestValidateConfig:
    """Test cases for validate_config decorator."""

    def test_validate_config_with_valid_config(self) -> None:
        """Test validate_config with valid configuration."""

        # Create mock config object with required attributes
        class MockConfig:
            api_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
            timeout = 30

        @validate_config(["api_url", "timeout"])
        def function_requiring_config(__config: MockConfig) -> str:
            return "config validated"

        result = function_requiring_config(MockConfig())
        if result != "config validated":
            msg: str = f"Expected {'config validated'}, got {result}"
            raise AssertionError(msg)

    def test_validate_config_with_missing_keys(self) -> None:
        """Test validate_config with missing required keys."""
        with patch("flext_cli.decorators.FlextLogger.error") as mock_logger:
            # Create mock config object missing required attributes
            class MockConfig:
                api_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
                # missing timeout

            @validate_config(["api_url", "timeout"])
            def function_requiring_config(__config: MockConfig) -> str:
                return "config validated"

            result = function_requiring_config(MockConfig())
            # Validate that function returned None when validation failed
            validation_passed = result is None
            if not validation_passed:
                pytest.fail(f"Expected None, got {result}")
            # Mock logger assertion - only executed if validation passed
            if validation_passed:
                mock_logger.assert_called_once_with(
                    "Missing required configuration: timeout"
                )

    def test_validate_config_no_context(self) -> None:
        """Test validate_config when no config available."""
        with patch("flext_cli.decorators.FlextLogger.warning") as mock_logger:

            @validate_config(["api_url"])
            def function_requiring_config() -> str:
                return "config validated"

            result = (
                function_requiring_config()
            )  # No config provided - this is intentional for testing
            # Validate that function returned None when no config available
            validation_passed = result is None
            if not validation_passed:
                pytest.fail(f"Expected None, got {result}")
            # Mock logger assertion - only executed if validation passed
            if validation_passed:
                mock_logger.assert_called_once_with(
                    "Configuration not available for validation."
                )


class TestWithSpinner:
    """Test cases for with_spinner decorator."""

    def test_with_spinner_default_message(self) -> None:
        """Test with_spinner decorator with default message."""
        with patch("flext_cli.decorators.FlextLogger.info") as mock_logger:

            @with_spinner()
            def long_running_task() -> str:
                time.sleep(0.01)  # Simulate work
                return "task completed"

            result = long_running_task()
            if result != "task completed":
                msg: str = f"Expected {'task completed'}, got {result}"
                raise AssertionError(msg)
            # Verify that logger was called for start and completion
            assert mock_logger.call_count == 2
            mock_logger.assert_any_call("Starting: Processing...")
            mock_logger.assert_any_call("Completed: Processing...")

    def test_with_spinner_custom_message(self) -> None:
        """Test with_spinner decorator with custom message."""
        with patch("flext_cli.decorators.FlextLogger.info") as mock_logger:

            @with_spinner("Calculating results...")
            def calculation_task() -> str:
                time.sleep(0.01)
                return "calculation done"

            result = calculation_task()
            if result != "calculation done":
                msg: str = f"Expected {'calculation done'}, got {result}"
                raise AssertionError(msg)
            # Verify that logger was called for start and completion
            assert mock_logger.call_count == 2
            mock_logger.assert_any_call("Starting: Calculating results...")
            mock_logger.assert_any_call("Completed: Calculating results...")

    def test_with_spinner_exception_handling(self) -> None:
        """Test with_spinner decorator with exception handling."""
        with patch("flext_cli.decorators.FlextLogger.info") as mock_logger:

            @with_spinner("Processing...")
            def failing_task() -> str:
                msg = "task failed"
                raise ValueError(msg)

            with pytest.raises(ValueError, match="task failed"):
                failing_task()
            # Verify that logger was called for start (completion won't be called due to exception)
            assert mock_logger.call_count == 1
            mock_logger.assert_called_once_with("Starting: Processing...")


class TestDecoratorCombinations:
    """Test combinations of decorators."""

    def test_multiple_decorators(self) -> None:
        """Test combining multiple decorators."""
        with (
            patch("builtins.input") as mock_input,
            patch("flext_cli.decorators.time.time") as mock_time,
        ):
            mock_input.return_value = "y"
            mock_time.side_effect = [1000.0, 1001.0, 1002.0]

            @confirm_action("Proceed?")
            @measure_time(show_in_output=False)
            @retry(max_attempts=2)
            def complex_function() -> str:
                return "all decorators applied"

            result = complex_function()
            if result != "all decorators applied":
                msg: str = f"Expected {'all decorators applied'}, got {result}"
                raise AssertionError(msg)

    def test_decorator_order_preservation(self) -> None:
        """Test that decorator order is preserved."""

        @measure_time(show_in_output=False)
        @retry(max_attempts=1)
        def decorated_function() -> str:
            """A decorated function."""
            return "result"

        # Function should still be callable and maintain behavior
        assert callable(decorated_function)
        if decorated_function() != "result":
            msg: str = f"Expected {'result'}, got {decorated_function()}"
            raise AssertionError(msg)
        assert decorated_function.__doc__ == "A decorated function."
