"""Tests for core base functionality in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import asyncio
import io

import pytest
from flext_core import FlextResult

from flext_cli import handle_service_result
from flext_cli.context import FlextCliContext

# Constants
EXPECTED_DATA_COUNT = 3


class TestCLIContext:
    """Test cases for FlextCliContext."""

    def test_context_creation(self, cli_context: FlextCliContext) -> None:
        """Test CLI context creation."""
        if cli_context.profile != "test":
            msg = f"Expected {'test'}, got {cli_context.profile}"
            raise AssertionError(msg)
        assert cli_context.output_format == "json"
        if not (cli_context.debug):
            msg = f"Expected True, got {cli_context.debug}"
            raise AssertionError(msg)
        if cli_context.quiet:
            msg = f"Expected False, got {cli_context.quiet}"
            raise AssertionError(msg)
        if not (cli_context.verbose):
            msg = f"Expected True, got {cli_context.verbose}"
            raise AssertionError(msg)
        assert cli_context.no_color is True

    def test_context_defaults(self) -> None:
        """Test CLI context with defaults."""
        context = FlextCliContext.create_with_params()
        if context.profile != "default":
            msg = f"Expected {'default'}, got {context.profile}"
            raise AssertionError(msg)
        assert context.output_format == "table"
        if context.debug:
            msg = f"Expected False, got {context.debug}"
            raise AssertionError(msg)
        assert context.quiet is False
        if context.verbose:
            msg = f"Expected False, got {context.verbose}"
            raise AssertionError(msg)
        assert context.no_color is False

    def test_context_immutability(self, cli_context: FlextCliContext) -> None:
        """Test CLI context immutability (FlextModels pattern)."""
        # Should be immutable as FlextModels - expect ValueError for frozen instance
        with pytest.raises(ValueError, match="Cannot modify immutable FlextCliContext"):
            cli_context.profile = "new-profile"

    def test_context_validation_empty_profile(self) -> None:
        """Test CLI context validation with empty profile."""
        with pytest.raises(ValueError, match="Profile cannot be empty"):
            FlextCliContext.create_with_params(profile="")

    def test_context_validation_invalid_output_format(self) -> None:
        """Test CLI context validation with invalid output format."""
        with pytest.raises(ValueError, match="Output format must be one of"):
            FlextCliContext.create_with_params(output_format="invalid_format")

    def test_context_validation_quiet_and_verbose(self) -> None:
        """Test CLI context validation with both quiet and verbose."""
        with pytest.raises(
            ValueError,
            match="Cannot have both quiet and verbose modes enabled",
        ):
            FlextCliContext.create_with_params(quiet=True, verbose=True)


class TestHandleServiceResult:
    """Test cases for handle_service_result decorator."""

    def test_successful_result_handling(self) -> None:
        """Test handling of successful FlextResult."""

        @handle_service_result
        def success_function() -> FlextResult[str]:
            return FlextResult[str].ok("success data")

        result = success_function()
        if result != "success data":
            msg = f"Expected {'success data'}, got {result}"
            raise AssertionError(msg)

    def test_failed_result_handling(self) -> None:
        """Test handling of failed FlextResult."""
        # Capture console output to verify error printing
        io.StringIO()

        @handle_service_result
        def fail_function() -> FlextResult[str]:
            return FlextResult[str].fail("error message")

        result = fail_function()

        assert result is None
        # The error should be printed to the console (no need to mock)

    def test_non_result_passthrough(self) -> None:
        """Test passthrough of non-FlextResult values."""

        @handle_service_result
        def regular_function() -> str:
            return "regular data"

        result = regular_function()
        if result != "regular data":
            msg = f"Expected {'regular data'}, got {result}"
            raise AssertionError(msg)

    def test_exception_handling(self) -> None:
        """Test exception handling in decorator."""

        @handle_service_result
        def exception_function() -> str:
            msg = "test exception"
            raise ValueError(msg)

        # Exception should be re-raised and error should be printed
        with pytest.raises(ValueError, match="test exception"):
            exception_function()

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test that decorator preserves function metadata."""

        @handle_service_result
        def documented_function() -> str:
            """A documented function."""
            return "result"

        if documented_function.__name__ != "documented_function":
            msg = (
                f"Expected {'documented_function'}, got {documented_function.__name__}"
            )
            raise AssertionError(
                msg,
            )
        assert documented_function.__doc__ == "A documented function."

    def test_decorator_with_arguments(self) -> None:
        """Test decorator with function arguments."""

        @handle_service_result
        def function_with_args(arg1: str, arg2: int, kwarg1: str = "default") -> str:
            return f"{arg1}-{arg2}-{kwarg1}"

        result = function_with_args("test", 42, kwarg1="custom")
        if result != "test-42-custom":
            msg = f"Expected {'test-42-custom'}, got {result}"
            raise AssertionError(msg)

    def test_result_with_complex_data(self) -> None:
        """Test handling FlextResult with complex data types."""

        @handle_service_result
        def complex_data_function() -> FlextResult[dict[str, object]]:
            return FlextResult[dict[str, object]].ok(
                {
                    "data": [1, 2, 3],
                    "metadata": {"count": 3, "type": "list"},
                    "nested": {"deep": {"value": "found"}},
                },
            )

        result = complex_data_function()

        assert isinstance(result, dict)
        if result["data"] != [1, 2, 3]:
            msg = f"Expected {[1, 2, 3]}, got {result['data']}"
            raise AssertionError(msg)
        assert result["metadata"]["count"] == EXPECTED_DATA_COUNT
        if result["nested"]["deep"]["value"] != "found":
            msg = f"Expected {'found'}, got {result['nested']['deep']['value']}"
            raise AssertionError(
                msg,
            )

    def test_async_function_compatibility(self) -> None:
        """Test decorator compatibility with async functions."""

        @handle_service_result
        async def async_function() -> FlextResult[str]:
            await asyncio.sleep(0.01)  # Small delay to test async
            return FlextResult[str].ok("async result")

        async def test_runner() -> None:
            async_result = await async_function()
            result = async_result if async_result is not None else None
            if result != "async result":
                msg = f"Expected {'async result'}, got {result}"
                raise AssertionError(msg)

        # Run the async test
        asyncio.run(test_runner())

    def test_async_failed_result_handling(self) -> None:
        """Test async handling of failed FlextResult - REAL functionality."""

        @handle_service_result
        async def async_fail_function() -> FlextResult[str]:
            await asyncio.sleep(0.01)
            return FlextResult[str].fail("async error message")

        async def test_runner() -> None:
            async_result = await async_fail_function()
            result = async_result if async_result is not None else None
            assert result is None
            # Error should be printed to console (no need to mock)

        # Run the async test
        asyncio.run(test_runner())

    def test_async_exception_handling(self) -> None:
        """Test async exception handling in decorator - REAL functionality."""

        @handle_service_result
        async def async_exception_function() -> str:
            await asyncio.sleep(0.01)
            msg = "async test exception"
            raise ValueError(msg)

        async def test_runner() -> None:
            # Exception should be re-raised and error should be printed
            async_result = await async_exception_function()
            if async_result is not None:
                with pytest.raises(ValueError, match="async test exception"):
                    await async_result

        # Run the async test
        asyncio.run(test_runner())

    def test_async_non_result_passthrough(self) -> None:
        """Test async passthrough of non-FlextResult values."""

        @handle_service_result
        async def async_regular_function() -> str:
            await asyncio.sleep(0.01)
            return "async regular data"

        async def test_runner() -> None:
            async_result = await async_regular_function()
            result = async_result if async_result is not None else None
            if result != "async regular data":
                msg = f"Expected {'async regular data'}, got {result}"
                raise AssertionError(msg)

        # Run the async test
        asyncio.run(test_runner())
