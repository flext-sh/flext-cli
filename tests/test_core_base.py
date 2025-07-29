"""Tests for core base functionality in FLEXT CLI Library.

# Constants
EXPECTED_DATA_COUNT = 3

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import asyncio
import asyncio
import asyncio


from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_cli.core.base import CLIContext, handle_service_result
from flext_core.result import FlextResult
from pydantic import ValidationError


class TestCLIContext:
    """Test cases for CLIContext."""

    def test_context_creation(self, cli_context: CLIContext) -> None:
        """Test CLI context creation."""
        if cli_context.profile != "test":
            raise AssertionError(f"Expected {"test"}, got {cli_context.profile}")
        assert cli_context.output_format == "json"
        if not (cli_context.debug):
            raise AssertionError(f"Expected True, got {cli_context.debug}")
        if cli_context.quiet:
            raise AssertionError(f"Expected False, got {cli_context.quiet}")\ n        if not (cli_context.verbose):
            raise AssertionError(f"Expected True, got {cli_context.verbose}")
        assert cli_context.no_color is True

    def test_context_defaults(self) -> None:
        """Test CLI context with defaults."""
        context = CLIContext()
        if context.profile != "default":
            raise AssertionError(f"Expected {"default"}, got {context.profile}")
        assert context.output_format == "table"
        if context.debug:
            raise AssertionError(f"Expected False, got {context.debug}")\ n        assert context.quiet is False
        if context.verbose:
            raise AssertionError(f"Expected False, got {context.verbose}")\ n        assert context.no_color is False

    def test_context_immutability(self, cli_context: CLIContext) -> None:
        """Test CLI context immutability (FlextValueObject pattern)."""
        # Should be immutable as FlextValueObject - expect ValidationError for frozen instance
        with pytest.raises(ValidationError):
            cli_context.profile = "new-profile"  # type: ignore[misc]

    def test_context_validation_empty_profile(self) -> None:
        """Test CLI context validation with empty profile."""
        with pytest.raises(ValueError, match="Profile cannot be empty"):
            CLIContext(profile="")

    def test_context_validation_invalid_output_format(self) -> None:
        """Test CLI context validation with invalid output format."""
        with pytest.raises(ValueError, match="Output format must be one of"):
            CLIContext(output_format="invalid_format")

    def test_context_validation_quiet_and_verbose(self) -> None:
        """Test CLI context validation with both quiet and verbose."""
        with pytest.raises(
            ValueError, match="Cannot have both quiet and verbose modes enabled"
        ):
            CLIContext(quiet=True, verbose=True)


class TestHandleServiceResult:
    """Test cases for handle_service_result decorator."""

    def test_successful_result_handling(self) -> None:
        """Test handling of successful FlextResult."""

        @handle_service_result
        def success_function() -> FlextResult[str]:
            return FlextResult.ok("success data")

        result = success_function()
        if result != "success data":
            raise AssertionError(f"Expected {"success data"}, got {result}")

    @patch("flext_cli.core.base.Console")
    def test_failed_result_handling(self, mock_console_class: Mock) -> None:
        """Test handling of failed FlextResult."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        @handle_service_result
        def fail_function() -> FlextResult[str]:
            return FlextResult.fail("error message")

        result = fail_function()

        assert result is None
        mock_console.print.assert_called_once_with("[red]Error: error message[/red]")

    def test_non_result_passthrough(self) -> None:
        """Test passthrough of non-FlextResult values."""

        @handle_service_result
        def regular_function() -> str:
            return "regular data"

        result = regular_function()
        if result != "regular data":
            raise AssertionError(f"Expected {"regular data"}, got {result}")

    @patch("flext_cli.core.base.Console")
    @patch("flext_cli.core.base.get_logger")
    def test_exception_handling(
        self,
        mock_get_logger: Mock,
        mock_console_class: Mock,
    ) -> None:
        """Test exception handling in decorator."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @handle_service_result
        def exception_function() -> str:
            msg = "test exception"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="test exception"):
            exception_function()

        mock_console.print.assert_called_once_with("[red]Error: test exception[/red]")
        mock_logger.exception.assert_called_once_with(
            "Unhandled exception in CLI command",
        )

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test that decorator preserves function metadata."""

        @handle_service_result
        def documented_function() -> str:
            """A documented function."""
            return "result"

        if documented_function.__name__ != "documented_function":

            raise AssertionError(f"Expected {"documented_function"}, got {documented_function.__name__}")
        assert documented_function.__doc__ == "A documented function."

    def test_decorator_with_arguments(self) -> None:
        """Test decorator with function arguments."""

        @handle_service_result
        def function_with_args(arg1: str, arg2: int, kwarg1: str = "default") -> str:
            return f"{arg1}-{arg2}-{kwarg1}"

        result = function_with_args("test", 42, kwarg1="custom")
        if result != "test-42-custom":
            raise AssertionError(f"Expected {"test-42-custom"}, got {result}")

    def test_result_with_complex_data(self) -> None:
        """Test handling FlextResult with complex data types."""

        @handle_service_result
        def complex_data_function() -> FlextResult[dict[str, any]]:
            return FlextResult.ok(
                {
                    "data": [1, 2, 3],
                    "metadata": {"count": 3, "type": "list"},
                    "nested": {"deep": {"value": "found"}},
                }
            )

        result = complex_data_function()

        assert isinstance(result, dict)
        if result["data"] != [1, 2, 3]:
            raise AssertionError(f"Expected {[1, 2, 3]}, got {result["data"]}")
        assert result["metadata"]["count"] == EXPECTED_DATA_COUNT
        if result["nested"]["deep"]["value"] != "found":
            raise AssertionError(f"Expected {"found"}, got {result["nested"]["deep"]["value"]}")

    def test_async_function_compatibility(self) -> None:
        """Test decorator compatibility with async functions."""


        @handle_service_result
        async def async_function() -> FlextResult[str]:
            await asyncio.sleep(0.01)  # Small delay to test async
            return FlextResult.ok("async result")

        async def test_runner() -> None:
            result = await async_function()
            if result != "async result":
                raise AssertionError(f"Expected {"async result"}, got {result}")

        # Run the async test
        asyncio.run(test_runner())

    @patch("flext_cli.core.base.Console")
    def test_async_failed_result_handling(self, mock_console_class: Mock) -> None:
        """Test async handling of failed FlextResult."""


        mock_console = Mock()
        mock_console_class.return_value = mock_console

        @handle_service_result
        async def async_fail_function() -> FlextResult[str]:
            await asyncio.sleep(0.01)
            return FlextResult.fail("async error message")

        async def test_runner() -> None:
            result = await async_fail_function()
            assert result is None
            mock_console.print.assert_called_once_with(
                "[red]Error: async error message[/red]"
            )

        # Run the async test
        asyncio.run(test_runner())

    @patch("flext_cli.core.base.Console")
    @patch("flext_cli.core.base.get_logger")
    def test_async_exception_handling(
        self,
        mock_get_logger: Mock,
        mock_console_class: Mock,
    ) -> None:
        """Test async exception handling in decorator."""
        import asyncio

        mock_console = Mock()
        mock_console_class.return_value = mock_console
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @handle_service_result
        async def async_exception_function() -> str:
            await asyncio.sleep(0.01)
            msg = "async test exception"
            raise ValueError(msg)

        async def test_runner() -> None:
            with pytest.raises(ValueError, match="async test exception"):
                await async_exception_function()

            mock_console.print.assert_called_once_with(
                "[red]Error: async test exception[/red]"
            )
            mock_logger.exception.assert_called_once_with(
                "Unhandled exception in CLI command",
            )

        # Run the async test
        asyncio.run(test_runner())

    def test_async_non_result_passthrough(self) -> None:
        """Test async passthrough of non-FlextResult values."""


        @handle_service_result
        async def async_regular_function() -> str:
            await asyncio.sleep(0.01)
            return "async regular data"

        async def test_runner() -> None:
            result = await async_regular_function()
            if result != "async regular data":
                raise AssertionError(f"Expected {"async regular data"}, got {result}")

        # Run the async test
        asyncio.run(test_runner())
