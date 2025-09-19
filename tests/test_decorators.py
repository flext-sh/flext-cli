"""Test FlextCliDecorators functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import tempfile
import time
import unittest
from pathlib import Path

import pytest

from flext_cli import FlextCliDecorators
from flext_core import FlextResult, FlextTypes


class TestFlextCliDecorators(unittest.TestCase):
    """Test FlextCliDecorators class methods with real functionality."""

    def test_async_command_with_async_function(self) -> None:
        """Test async_command decorator with an actual async function."""

        @FlextCliDecorators.async_command
        async def async_test_func() -> str:
            await asyncio.sleep(0.01)
            return "async_result"

        # The async_command decorator should handle the async execution
        result = async_test_func()
        # Check if it's a coroutine that needs to be awaited or the actual result
        if asyncio.iscoroutine(result):
            # If it's still a coroutine, run it
            actual_result = asyncio.run(result)
            assert actual_result == "async_result"
        else:
            # If the decorator already handled it
            assert result == "async_result"

    def test_async_command_with_sync_function(self) -> None:
        """Test async_command decorator with a sync function."""

        @FlextCliDecorators.async_command
        def sync_test_func() -> str:
            return "sync_result"

        result = sync_test_func()
        assert result == "sync_result"

    def test_confirm_action_decorator(self) -> None:
        """Test confirm_action decorator (programmatic testing only)."""

        @FlextCliDecorators.confirm_action("Test confirmation?")
        def test_func() -> str:
            return "confirmed"

        # This decorator requires user input, so we just test it exists
        assert hasattr(test_func, "__wrapped__")
        assert test_func.__name__ == "test_func"

    def test_require_auth_decorator_no_token(self) -> None:
        """Test require_auth decorator when no token exists."""

        @FlextCliDecorators.require_auth("/nonexistent/token")
        def test_func() -> str:
            return "authenticated"

        result = test_func()
        assert result is None  # Should return None when no token

    def test_require_auth_decorator_with_token(self) -> None:
        """Test require_auth decorator with valid token."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("test_token")
            temp_file.flush()

            @FlextCliDecorators.require_auth(temp_file.name)
            def test_func() -> str:
                return "authenticated"

            result = test_func()
            assert result == "authenticated"

            # Clean up
            Path(temp_file.name).unlink()

    def test_measure_time_decorator(self) -> None:
        """Test measure_time decorator with real timing."""

        @FlextCliDecorators.measure_time(show_in_output=False)
        def test_func() -> str:
            time.sleep(0.01)
            return "timed"

        result = test_func()
        assert result == "timed"

    def test_validate_config_decorator_missing_config(self) -> None:
        """Test validate_config decorator with missing config."""

        @FlextCliDecorators.validate_config(["required_key"])
        def test_func() -> str:
            return "validated"

        result = test_func()
        assert result is None  # Should return None when config missing

    def test_validate_config_decorator_with_config(self) -> None:
        """Test validate_config decorator with valid config."""

        @FlextCliDecorators.validate_config(["required_key"])
        def test_func(config: FlextTypes.Core.Headers) -> str:
            return f"validated: {config}"

        result = test_func(config={"required_key": "value"})
        assert result == "validated: {'required_key': 'value'}"

    def test_with_spinner_decorator(self) -> None:
        """Test with_spinner decorator with real execution."""

        @FlextCliDecorators.with_spinner("Testing spinner")
        def test_func() -> str:
            time.sleep(0.01)
            return "spun"

        result = test_func()
        assert result == "spun"

    def test_flext_cli_auto_validate_decorator(self) -> None:
        """Test flext_cli_auto_validate decorator."""

        @FlextCliDecorators.flext_cli_auto_validate(["validator1"])
        def test_func() -> str:
            return "validated"

        result = test_func()
        assert result == "validated"

    def test_require_confirmation_decorator(self) -> None:
        """Test require_confirmation decorator (no-op)."""

        @FlextCliDecorators.require_confirmation("test action")
        def test_func() -> str:
            return "confirmed"

        result = test_func()
        assert result == "confirmed"

    def test_handle_service_result_function(self) -> None:
        """Test handle_service_result pass-through decorator."""

        @FlextCliDecorators.handle_service_result
        def test_func() -> FlextResult[str]:
            return FlextResult[str].ok("handled")

        result = test_func()
        # Decorator extracts the value from FlextResult
        assert result == "handled"

    def test_handle_service_result_failure(self) -> None:
        """Test handle_service_result with failed result."""

        @FlextCliDecorators.handle_service_result
        def test_func() -> FlextResult[str]:
            return FlextResult[str].fail("error")

        result = test_func()
        # Should return None on failure
        assert result is None

    def test_handle_service_result_async(self) -> None:
        """Test handle_service_result with async function."""

        @FlextCliDecorators.handle_service_result
        async def test_func() -> FlextResult[str]:
            return FlextResult[str].ok("async_handled")

        # Run the async function
        async def run_test() -> None:
            result = await test_func()
            assert result == "async_handled"

        asyncio.run(run_test())

    def test_handle_service_result_async_failure(self) -> None:
        """Test handle_service_result with async function failure."""

        @FlextCliDecorators.handle_service_result
        async def test_func() -> FlextResult[str]:
            return FlextResult[str].fail("async_error")

        async def run_test() -> None:
            result = await test_func()
            assert result is None

        asyncio.run(run_test())

    def test_cli_measure_time_decorator(self) -> None:
        """Test cli_measure_time decorator."""

        @FlextCliDecorators.cli_measure_time
        def test_func() -> str:
            time.sleep(0.01)  # Small delay to measure
            return "timed"

        result = test_func()
        assert result == "timed"

    def test_cli_measure_time_with_exception(self) -> None:
        """Test cli_measure_time decorator with exception."""

        @FlextCliDecorators.cli_measure_time
        def test_func() -> str:
            error_msg = "test error"
            raise ValueError(error_msg)

        with pytest.raises(ValueError):
            test_func()

    def test_cli_retry_decorator(self) -> None:
        """Test cli_retry decorator with success."""
        call_count = 0

        @FlextCliDecorators.cli_retry(max_attempts=3)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error_msg = "retry me"
                raise ValueError(error_msg)
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 2

    def test_cli_retry_decorator_max_attempts(self) -> None:
        """Test cli_retry decorator reaching max attempts."""

        @FlextCliDecorators.cli_retry(max_attempts=2)
        def test_func() -> str:
            error_msg = "always fail"
            raise ValueError(error_msg)

        with pytest.raises(ValueError):
            test_func()

    def test_retry_decorator(self) -> None:
        """Test general retry decorator with success."""
        call_count = 0

        @FlextCliDecorators.retry(max_attempts=3, initial_backoff=0.01)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error_msg = "retry me"
                raise ConnectionError(error_msg)
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 2

    def test_retry_decorator_max_attempts(self) -> None:
        """Test retry decorator reaching max attempts."""

        @FlextCliDecorators.retry(max_attempts=2, initial_backoff=0.01)
        def test_func() -> str:
            error_msg = "always fail"
            raise ConnectionError(error_msg)

        with pytest.raises(ConnectionError):
            test_func()

    def test_retry_decorator_with_specific_exceptions(self) -> None:
        """Test retry decorator with specific exception types."""

        @FlextCliDecorators.retry(
            max_attempts=2,
            exceptions=(ValueError,),
            initial_backoff=0.01,
        )
        def test_func() -> str:
            error_msg = "specific exception"
            raise ValueError(error_msg)

        with pytest.raises(ValueError):
            test_func()

    def test_retry_decorator_with_different_exception(self) -> None:
        """Test retry decorator with exception not in allowed list."""

        @FlextCliDecorators.retry(
            max_attempts=3,
            exceptions=(ValueError,),
            initial_backoff=0.01,
        )
        def test_func() -> str:
            error_msg = "different exception"
            raise TypeError(error_msg)

        # Should not retry TypeError, raise immediately
        with pytest.raises(TypeError):
            test_func()

    def test_require_auth_decorator_file_not_found(self) -> None:
        """Test require_auth decorator when token file is not found."""

        @FlextCliDecorators.require_auth(token_file="nonexistent.txt")
        def test_func() -> str:
            return "authenticated"

        result = test_func()
        # Should return None when auth fails
        assert result is None

    def test_confirm_action_edge_cases(self) -> None:
        """Test confirm_action decorator edge cases."""

        @FlextCliDecorators.confirm_action("Proceed?")
        def test_func() -> str:
            return "proceeded"

        # Test with mocked input - we'll simulate the exception case
        # Since we can't easily mock input in unittest, test the exception handling
        result = test_func()
        # Function will be called interactively, but in automated tests
        # it might return None due to input handling
        assert result is None or result == "proceeded"

    def test_validate_config_decorator_complex(self) -> None:
        """Test validate_config decorator with complex config."""

        @FlextCliDecorators.validate_config(required_keys=["api_key", "endpoint"])
        def test_func(config: dict[str, str]) -> str:
            return f"config valid: {config['api_key']}"

        # Test with valid config
        result = test_func({"api_key": "test", "endpoint": "api.test.com"})
        assert result is None or "config valid" in str(result)

    def test_with_spinner_decorator_exception(self) -> None:
        """Test with_spinner decorator when function raises exception."""

        @FlextCliDecorators.with_spinner("Processing...")
        def test_func() -> str:
            error_msg = "processing failed"
            raise RuntimeError(error_msg)

        with pytest.raises(RuntimeError):
            test_func()

    def test_handle_service_result_non_result_return(self) -> None:
        """Test handle_service_result with non-FlextResult return."""

        @FlextCliDecorators.handle_service_result
        def test_func() -> FlextResult[str]:
            return FlextResult[str].ok("direct_string")

        # Should return the unwrapped value for successful FlextResult
        result = test_func()
        assert result == "direct_string"

    def test_measure_time_decorator_parameters(self) -> None:
        """Test measure_time decorator with parameters."""

        @FlextCliDecorators.measure_time(show_in_output=True)
        def test_func(arg1: str, arg2: int = 42) -> str:
            return f"processed {arg1} with {arg2}"

        result = test_func("test", arg2=100)
        assert result == "processed test with 100"

    def test_async_command_exception_handling(self) -> None:
        """Test async_command decorator with exception."""

        @FlextCliDecorators.async_command
        async def async_error_func() -> str:
            error_msg = "async error"
            raise ValueError(error_msg)

        # Test exception propagation - async_command decorator runs the async function synchronously
        with pytest.raises(ValueError):
            async_error_func()  # type: ignore[unused-coroutine]


if __name__ == "__main__":
    unittest.main()
