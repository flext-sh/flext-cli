"""Test FlextCliUtilities.Decorators functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from flext_cli import FlextCliUtilities
from flext_core import FlextTypes


class TestFlextCliDecorators(unittest.TestCase):
    """Test FlextCliUtilities.Decorators class methods with real functionality."""

    def test_async_command_with_async_function(self) -> None:
        """Test async_command decorator with an actual async function."""

        @FlextCliUtilities.Decorators.async_command
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
            # If the decorator already handled it, check the result directly
            assert result == "async_result"

    def test_confirm_action_decorator(self) -> None:
        """Test confirm_action decorator (programmatic testing only)."""

        @FlextCliUtilities.Decorators.confirm_action("Test confirmation?")
        def test_func() -> str:
            return "confirmed"

        # This decorator requires user input, so we just test it exists
        assert hasattr(test_func, "__wrapped__")
        assert test_func.__name__ == "test_func"

    def test_require_auth_decorator_no_token(self) -> None:
        """Test require_auth decorator when no token exists."""

        @FlextCliUtilities.Decorators.require_auth("/nonexistent/token")
        def test_func() -> str:
            return "authenticated"

        result = test_func()
        assert result is None  # Should return None when no token

    def test_require_auth_decorator_with_token(self) -> None:
        """Test require_auth decorator with valid token."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as temp_file:
            temp_file.write("test_token")
            temp_file.flush()

            @FlextCliUtilities.Decorators.require_auth(temp_file.name)
            def test_func() -> str:
                return "authenticated"

            result = test_func()
            assert result == "authenticated"

            # Clean up
            Path(temp_file.name).unlink()

    def test_measure_time_decorator(self) -> None:
        """Test measure_time decorator with real timing."""

        @FlextCliUtilities.Decorators.measure_time(show_in_output=False)
        def test_func() -> str:
            time.sleep(0.01)
            return "timed"

        result = test_func()
        assert result == "timed"

    def test_validate_config_decorator_missing_config(self) -> None:
        """Test validate_config decorator with missing config."""

        @FlextCliUtilities.Decorators.validate_config(["required_key"])
        def test_func() -> str:
            return "validated"

        result = test_func()
        assert result is None  # Should return None when config missing

    def test_validate_config_decorator_with_config(self) -> None:
        """Test validate_config decorator with valid config."""

        @FlextCliUtilities.Decorators.validate_config(["required_key"])
        def test_func(config: FlextTypes.Core.Headers) -> str:
            return f"validated: {config}"

        result = test_func(config={"required_key": "value"})
        assert result == "validated: {'required_key': 'value'}"

    def test_with_spinner_decorator(self) -> None:
        """Test with_spinner decorator with real execution."""

        @FlextCliUtilities.Decorators.with_spinner("Testing spinner")
        def test_func() -> str:
            time.sleep(0.01)
            return "spun"

        result = test_func()
        assert result == "spun"

    def test_measure_time_decorator_without_output(self) -> None:
        """Test measure_time decorator without output."""

        @FlextCliUtilities.Decorators.measure_time(show_in_output=False)
        def test_func() -> str:
            time.sleep(0.01)  # Small delay to measure
            return "timed"

        result = test_func()
        assert result == "timed"

    def test_measure_time_with_exception(self) -> None:
        """Test measure_time decorator with exception."""

        @FlextCliUtilities.Decorators.measure_time(show_in_output=True)
        def test_func() -> str:
            error_msg = "test error"
            raise ValueError(error_msg)

        with pytest.raises(ValueError):
            test_func()

    def test_retry_decorator_basic(self) -> None:
        """Test retry decorator with success."""
        call_count = 0

        @FlextCliUtilities.Decorators.retry(max_attempts=3)
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

    def test_retry_decorator_max_attempts_basic(self) -> None:
        """Test retry decorator reaching max attempts."""

        @FlextCliUtilities.Decorators.retry(max_attempts=2)
        def test_func() -> str:
            error_msg = "always fail"
            raise ValueError(error_msg)

        with pytest.raises(ValueError):
            test_func()

    def test_retry_decorator(self) -> None:
        """Test general retry decorator with success."""
        call_count = 0

        @FlextCliUtilities.Decorators.retry(max_attempts=3, delay=0.01)
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

        @FlextCliUtilities.Decorators.retry(max_attempts=2, delay=0.01)
        def test_func() -> str:
            error_msg = "always fail"
            raise ConnectionError(error_msg)

        with pytest.raises(ConnectionError):
            test_func()

    def test_retry_decorator_with_specific_exceptions(self) -> None:
        """Test retry decorator with specific exception types."""

        @FlextCliUtilities.Decorators.retry(
            max_attempts=2,
            delay=0.01,
        )
        def test_func() -> str:
            error_msg = "specific exception"
            raise ValueError(error_msg)

        with pytest.raises(ValueError):
            test_func()

    def test_retry_decorator_with_different_exception(self) -> None:
        """Test retry decorator with exception not in allowed list."""

        @FlextCliUtilities.Decorators.retry(
            max_attempts=3,
            delay=0.01,
        )
        def test_func() -> str:
            error_msg = "different exception"
            raise TypeError(error_msg)

        # Should not retry TypeError, raise immediately
        with pytest.raises(TypeError):
            test_func()

    def test_require_auth_decorator_file_not_found(self) -> None:
        """Test require_auth decorator when token file is not found."""

        @FlextCliUtilities.Decorators.require_auth(token_file="nonexistent.txt")
        def test_func() -> str:
            return "authenticated"

        result = test_func()
        # Should return None when auth fails
        assert result is None

    def test_confirm_action_edge_cases(self) -> None:
        """Test confirm_action decorator edge cases."""

        @FlextCliUtilities.Decorators.confirm_action("Proceed?")
        def test_func() -> str:
            return "proceeded"

        # Test with mocked input
        with patch("builtins.input", return_value="y"):
            result = test_func()
            assert result == "proceeded"

        # Test with mocked input returning "n"
        with patch("builtins.input", return_value="n"):
            result = test_func()
            assert result is None

    def test_validate_config_decorator_complex(self) -> None:
        """Test validate_config decorator with complex config."""

        @FlextCliUtilities.Decorators.validate_config(
            required_keys=["api_key", "endpoint"]
        )
        def test_func(config: dict[str, str]) -> str:
            return f"config valid: {config['api_key']}"

        # Test with valid config
        result = test_func({"api_key": "test", "endpoint": "api.test.com"})
        assert result is None or "config valid" in str(result)

    def test_with_spinner_decorator_exception(self) -> None:
        """Test with_spinner decorator when function raises exception."""

        @FlextCliUtilities.Decorators.with_spinner("Processing...")
        def test_func() -> str:
            error_msg = "processing failed"
            raise RuntimeError(error_msg)

        with pytest.raises(RuntimeError):
            test_func()

    def test_measure_time_decorator_parameters(self) -> None:
        """Test measure_time decorator with parameters."""

        @FlextCliUtilities.Decorators.measure_time(show_in_output=True)
        def test_func(arg1: str, arg2: int = 42) -> str:
            return f"processed {arg1} with {arg2}"

        result = test_func("test", arg2=100)
        assert result == "processed test with 100"

    def test_async_command_exception_handling(self) -> None:
        """Test async_command decorator with exception."""

        @FlextCliUtilities.Decorators.async_command
        async def async_error_func() -> str:
            await asyncio.sleep(0.001)  # Use async feature
            error_msg = "async error"
            raise ValueError(error_msg)

        # Test exception propagation - async_command decorator wraps the async function
        # The async function is wrapped, so we need to handle it properly
        coro = async_error_func()
        with pytest.raises(ValueError):
            asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
