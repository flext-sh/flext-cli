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

from flext_core import FlextResult, FlextTypes

from flext_cli import (
    FlextCliDecorators,
    handle_service_result,
)


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

        @handle_service_result
        def test_func() -> FlextResult[str]:
            return FlextResult[str].ok("handled")

        result = test_func()
        # Decorator extracts the value from FlextResult
        assert result == "handled"


if __name__ == "__main__":
    unittest.main()
