"""Comprehensive real functionality tests for decorators.py module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

NO MOCKING - All tests execute real functionality and validate actual business logic.
Following user requirement: "pare de ficar mockando tudo!"

These tests systematically eliminate ALL 54+ mock instances from decorator tests
and replace them with comprehensive real functionality validation.
"""

from __future__ import annotations

import asyncio
import tempfile
import time
import unittest
from pathlib import Path

import pytest
from flext_core import FlextResult

from flext_cli.decorators import (
    async_command,
    cli_cache_result,
    cli_confirm_decorator,
    cli_enhanced,
    cli_file_operation,
    cli_handle_keyboard_interrupt,
    cli_log_execution,
    cli_measure_time,
    cli_retry,
    cli_spinner,
    cli_validate_inputs,
)

# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI-ENHANCED DECORATOR
# =============================================================================


class TestCliEnhancedDecorator(unittest.TestCase):
    """Test cli_enhanced decorator with real functionality execution."""

    def test_cli_enhanced_basic_function_execution(self) -> None:
        """Test cli_enhanced decorator with basic function."""

        @cli_enhanced
        def simple_function(x: int, y: int) -> int:
            return x + y

        result = simple_function(5, 3)
        assert result == 8

    def test_cli_enhanced_with_validation_enabled(self) -> None:
        """Test cli_enhanced decorator with input validation enabled."""

        @cli_enhanced(validate_inputs=True)
        def validated_function(name: str) -> str:
            return f"Hello, {name}!"

        result = validated_function("Alice")
        assert result == "Hello, Alice!"

    def test_cli_enhanced_with_time_measurement(self) -> None:
        """Test cli_enhanced decorator with execution time measurement."""

        @cli_enhanced(measure_time=True)
        def timed_function() -> str:
            time.sleep(0.01)  # 10ms delay
            return "completed"

        result = timed_function()
        assert result == "completed"

    def test_cli_enhanced_with_execution_logging(self) -> None:
        """Test cli_enhanced decorator with execution logging."""

        @cli_enhanced(log_execution=True)
        def logged_function(data: str) -> str:
            return f"processed: {data}"

        result = logged_function("test_data")
        assert result == "processed: test_data"

    def test_cli_enhanced_keyboard_interrupt_handling(self) -> None:
        """Test cli_enhanced decorator handles keyboard interrupts gracefully."""

        @cli_enhanced(handle_keyboard_interrupt=True)
        def interruptible_function() -> str:
            return "normal_execution"

        # Normal execution should work
        result = interruptible_function()
        assert result == "normal_execution"

    def test_cli_enhanced_all_options_enabled(self) -> None:
        """Test cli_enhanced decorator with all options enabled."""

        @cli_enhanced(
            validate_inputs=True,
            handle_keyboard_interrupt=True,
            measure_time=True,
            log_execution=True,
        )
        def comprehensive_function(value: int) -> int:
            return value * 2

        result = comprehensive_function(21)
        assert result == 42

    def test_cli_enhanced_return_types_preserved(self) -> None:
        """Test cli_enhanced decorator preserves return types correctly."""

        @cli_enhanced
        def return_string() -> str:
            return "string result"

        @cli_enhanced
        def return_int() -> int:
            return 42

        @cli_enhanced
        def return_list() -> list[str]:
            return ["a", "b", "c"]

        assert return_string() == "string result"
        assert return_int() == 42
        assert return_list() == ["a", "b", "c"]

    def test_cli_enhanced_exception_propagation(self) -> None:
        """Test cli_enhanced decorator properly propagates exceptions."""

        @cli_enhanced
        def failing_function() -> None:
            msg = "Test error"
            raise ValueError(msg)

        with pytest.raises(RuntimeError, match="Test error"):
            failing_function()


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI KEYBOARD INTERRUPT HANDLING
# =============================================================================


class TestCliKeyboardInterruptHandling(unittest.TestCase):
    """Test cli_handle_keyboard_interrupt decorator with real scenarios."""

    def test_cli_handle_keyboard_interrupt_normal_execution(self) -> None:
        """Test keyboard interrupt handler during normal execution."""

        @cli_handle_keyboard_interrupt
        def normal_function(value: str) -> str:
            return f"processed: {value}"

        result = normal_function("test_data")
        assert result == "processed: test_data"

    def test_cli_handle_keyboard_interrupt_long_running_function(self) -> None:
        """Test keyboard interrupt handler with long-running function."""

        @cli_handle_keyboard_interrupt
        def long_running_function() -> str:
            # Simulate work without actual delay for fast tests
            counter = 0
            for i in range(1000):
                counter += i
            return f"completed: {counter}"

        result = long_running_function()
        assert "completed:" in result
        assert isinstance(result, str)

    def test_cli_handle_keyboard_interrupt_exception_propagation(self) -> None:
        """Test keyboard interrupt handler propagates non-KeyboardInterrupt exceptions."""

        @cli_handle_keyboard_interrupt
        def exception_function() -> None:
            msg = "Regular exception"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Regular exception"):
            exception_function()


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI RETRY MECHANISM
# =============================================================================


class TestCliRetry(unittest.TestCase):
    """Test cli_retry decorator with real failure/recovery scenarios."""

    def test_cli_retry_eventually_succeeds(self) -> None:
        """Test retry decorator when function eventually succeeds."""
        call_count = 0

        @cli_retry(max_attempts=3, delay=0.01)
        def eventually_successful_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "Not ready yet"
                raise ValueError(msg)
            return "success"

        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 3

    def test_cli_retry_max_attempts_exceeded(self) -> None:
        """Test retry decorator when max attempts are exceeded."""

        @cli_retry(max_attempts=2, delay=0.001)
        def always_failing_function() -> None:
            msg = "Always fails"
            raise ConnectionError(msg)

        with pytest.raises(ConnectionError, match="Always fails"):
            always_failing_function()

    def test_cli_retry_no_retry_needed(self) -> None:
        """Test retry decorator when function succeeds immediately."""

        @cli_retry(max_attempts=3, delay=0.01)
        def immediate_success() -> int:
            return 42

        result = immediate_success()
        assert result == 42

    def test_cli_retry_different_exception_types(self) -> None:
        """Test retry decorator with different exception types."""
        attempt_count = 0

        @cli_retry(max_attempts=4, delay=0.001)
        def multi_exception_function() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                msg = "First attempt"
                raise ValueError(msg)
            if attempt_count == 2:
                msg = "Second attempt"
                raise RuntimeError(msg)
            if attempt_count == 3:
                msg = "Third attempt"
                raise ConnectionError(msg)
            return "finally succeeded"

        result = multi_exception_function()
        assert result == "finally succeeded"
        assert attempt_count == 4


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI EXECUTION TIME MEASUREMENT
# =============================================================================


class TestCliMeasureTime(unittest.TestCase):
    """Test cli_measure_time decorator with real timing."""

    def test_cli_measure_time_basic_function(self) -> None:
        """Test execution time measurement on basic function."""

        @cli_measure_time
        def timed_function() -> int:
            time.sleep(0.01)  # 10ms delay
            return 42

        result = timed_function()
        assert result == 42

    def test_cli_measure_time_fast_function(self) -> None:
        """Test execution time measurement on fast function."""

        @cli_measure_time
        def fast_function() -> str:
            return "immediate"

        result = fast_function()
        assert result == "immediate"

    def test_cli_measure_time_with_parameters(self) -> None:
        """Test execution time measurement with function parameters."""

        @cli_measure_time
        def parameterized_function(x: int, y: str) -> str:
            time.sleep(0.005)  # 5ms delay
            return f"{y}_{x}"

        result = parameterized_function(123, "test")
        assert result == "test_123"

    def test_cli_measure_time_exception_handling(self) -> None:
        """Test execution time measurement when function raises exception."""

        @cli_measure_time
        def exception_function() -> None:
            time.sleep(0.005)
            msg = "Planned failure"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Planned failure"):
            exception_function()

    def test_cli_measure_time_return_type_preservation(self) -> None:
        """Test execution time measurement preserves complex return types."""

        @cli_measure_time
        def complex_return_function() -> dict[str, list[int]]:
            time.sleep(0.001)
            return {"numbers": [1, 2, 3], "more_numbers": [4, 5, 6]}

        result = complex_return_function()
        assert isinstance(result, dict)
        assert result["numbers"] == [1, 2, 3]
        assert result["more_numbers"] == [4, 5, 6]


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI INPUT VALIDATION
# =============================================================================


class TestCliValidateInputs(unittest.TestCase):
    """Test cli_validate_inputs decorator with real validation scenarios."""

    def test_cli_validate_inputs_basic_function(self) -> None:
        """Test input validation with basic function."""

        @cli_validate_inputs
        def validated_function(name: str, age: int) -> str:
            return f"{name} is {age} years old"

        result = validated_function("Alice", 30)
        assert result == "Alice is 30 years old"

    def test_cli_validate_inputs_string_processing(self) -> None:
        """Test input validation with string processing."""

        @cli_validate_inputs
        def string_processor(text: str) -> str:
            return text.upper().strip()

        result = string_processor("  hello world  ")
        assert result == "HELLO WORLD"

    def test_cli_validate_inputs_complex_types(self) -> None:
        """Test input validation with complex types."""

        @cli_validate_inputs
        def process_data(
            items: list[str], metadata: dict[str, int]
        ) -> dict[str, object]:
            return {"count": len(items), "items": items, "metadata": metadata}

        result = process_data(["a", "b", "c"], {"version": 1})
        assert result["count"] == 3
        assert result["items"] == ["a", "b", "c"]
        assert result["metadata"]["version"] == 1

    def test_cli_validate_inputs_exception_handling(self) -> None:
        """Test input validation with exception scenarios."""

        @cli_validate_inputs
        def failing_validation() -> None:
            msg = "Validation failed"
            raise TypeError(msg)

        with pytest.raises(TypeError, match="Validation failed"):
            failing_validation()


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI CACHING MECHANISM
# =============================================================================


class TestCliCacheResult(unittest.TestCase):
    """Test cli_cache_result decorator with real caching behavior."""

    def test_cli_cache_result_basic_function_caching(self) -> None:
        """Test basic function result caching."""
        call_count = 0

        @cli_cache_result(ttl=1)
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x

        # First call
        result1 = expensive_function(5)
        assert result1 == 25
        assert call_count == 1

        # Second call with same arguments (should use cache)
        result2 = expensive_function(5)
        assert result2 == 25
        assert call_count == 1  # No additional call

        # Call with different arguments (should not use cache)
        result3 = expensive_function(6)
        assert result3 == 36
        assert call_count == 2

    def test_cli_cache_result_different_parameters(self) -> None:
        """Test cache behavior with different parameter combinations."""
        call_count = 0

        @cli_cache_result(ttl=60)  # Long TTL for testing
        def parameterized_function(x: int, y: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"{y}_{x}"

        # Different parameter combinations should each be cached separately
        result1 = parameterized_function(1, "hello")
        result2 = parameterized_function(2, "hello")
        result3 = parameterized_function(1, "world")
        result4 = parameterized_function(1, "hello")  # Same as first call

        assert result1 == "hello_1"
        assert result2 == "hello_2"
        assert result3 == "world_1"
        assert result4 == "hello_1"
        assert call_count == 3  # Fourth call used cache

    def test_cli_cache_result_complex_return_types(self) -> None:
        """Test caching with complex return types."""
        call_count = 0

        @cli_cache_result(ttl=1)
        def complex_function(key: str) -> dict[str, object]:
            nonlocal call_count
            call_count += 1
            return {
                "key": key,
                "timestamp": time.time(),
                "data": [1, 2, 3],
                "nested": {"value": 42},
            }

        result1 = complex_function("test")
        result2 = complex_function("test")  # Should use cache

        assert result1["key"] == "test"
        assert result2["key"] == "test"
        assert result1["timestamp"] == result2["timestamp"]  # Same object from cache
        assert call_count == 1


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI SPINNER
# =============================================================================


class TestCliSpinner(unittest.TestCase):
    """Test cli_spinner decorator with real spinner behavior."""

    def test_cli_spinner_basic_function(self) -> None:
        """Test spinner decorator with basic function."""

        @cli_spinner("Processing data...")
        def data_processing() -> str:
            time.sleep(0.01)  # Simulate work
            return "data processed"

        result = data_processing()
        assert result == "data processed"

    def test_cli_spinner_custom_message(self) -> None:
        """Test spinner decorator with custom message."""

        @cli_spinner("Custom processing message...")
        def custom_processing(items: int) -> int:
            time.sleep(0.005)
            return items * 2

        result = custom_processing(10)
        assert result == 20

    def test_cli_spinner_exception_handling(self) -> None:
        """Test spinner decorator handles exceptions properly."""

        @cli_spinner("Processing that will fail...")
        def failing_processing() -> None:
            time.sleep(0.001)
            msg = "Processing failed"
            raise RuntimeError(msg)

        with pytest.raises(RuntimeError, match="Processing failed"):
            failing_processing()

    def test_cli_spinner_complex_operations(self) -> None:
        """Test spinner decorator with complex operations."""

        @cli_spinner("Running complex operations...")
        def complex_operations() -> dict[str, object]:
            # Simulate multiple steps
            data = {}
            for step in range(5):
                time.sleep(0.001)  # Small delay per step
                data[f"step_{step}"] = step * step
            return data

        result = complex_operations()
        assert isinstance(result, dict)
        assert len(result) == 5
        assert result["step_2"] == 4


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI LOG EXECUTION
# =============================================================================


class TestCliLogExecution(unittest.TestCase):
    """Test cli_log_execution decorator with real logging."""

    def test_cli_log_execution_basic_function(self) -> None:
        """Test execution logging with basic function."""

        @cli_log_execution
        def logged_function(value: str) -> str:
            return f"processed: {value}"

        result = logged_function("test_input")
        assert result == "processed: test_input"

    def test_cli_log_execution_complex_function(self) -> None:
        """Test execution logging with complex function."""

        @cli_log_execution
        def complex_logged_function(data: dict[str, int]) -> dict[str, int]:
            return {k: v * 2 for k, v in data.items()}

        input_data = {"a": 1, "b": 2, "c": 3}
        result = complex_logged_function(input_data)
        assert result == {"a": 2, "b": 4, "c": 6}

    def test_cli_log_execution_exception_handling(self) -> None:
        """Test execution logging with exceptions."""

        @cli_log_execution
        def failing_logged_function() -> None:
            msg = "Logged failure"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Logged failure"):
            failing_logged_function()

    def test_cli_log_execution_async_function(self) -> None:
        """Test execution logging with async function."""

        @cli_log_execution
        async def async_logged_function(x: int) -> int:
            await asyncio.sleep(0.001)
            return x * 3

        async def run_test() -> None:
            result = await async_logged_function(5)
            assert result == 15

        asyncio.run(run_test())


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI FILE OPERATIONS
# =============================================================================


class TestCliFileOperation(unittest.TestCase):
    """Test cli_file_operation decorator with real file operations."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.txt"
        self.test_file.write_text("test content", encoding="utf-8")

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        if self.test_file.exists():
            self.test_file.unlink()
        if self.temp_dir.exists():
            self.temp_dir.rmdir()

    def test_cli_file_operation_read_file(self) -> None:
        """Test file operation decorator with file reading."""

        @cli_file_operation()
        def read_file_content(file_path: Path) -> str:
            return file_path.read_text(encoding="utf-8").strip()

        result = read_file_content(self.test_file)
        assert result == "test content"

    def test_cli_file_operation_write_file(self) -> None:
        """Test file operation decorator with file writing."""

        @cli_file_operation(backup=False)  # No backup for test
        def write_file_content(file_path: Path, content: str) -> bool:
            file_path.write_text(content, encoding="utf-8")
            return True

        new_file = self.temp_dir / "new_file.txt"
        result = write_file_content(new_file, "new content")

        assert result is True
        assert new_file.exists()
        assert new_file.read_text(encoding="utf-8") == "new content"

        # Cleanup
        new_file.unlink()

    def test_cli_file_operation_directory_listing(self) -> None:
        """Test file operation decorator with directory operations."""

        @cli_file_operation()
        def list_directory_files(dir_path: Path) -> list[str]:
            return [f.name for f in dir_path.iterdir() if f.is_file()]

        result = list_directory_files(self.temp_dir)
        assert "test.txt" in result


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR CLI CONFIRM
# =============================================================================


class TestCliConfirm(unittest.TestCase):
    """Test cli_confirm decorator with real confirmation scenarios."""

    def test_cli_confirm_basic_function(self) -> None:
        """Test confirm decorator with basic function."""

        # Note: cli_confirm typically requires user interaction,
        # so we test the decorator application without actual confirmation
        @cli_confirm_decorator("Are you sure?")
        def confirmed_function(value: int) -> int:
            return value * 2

        # This test verifies the decorator can be applied
        # Actual confirmation behavior would require user interaction
        assert hasattr(confirmed_function, "__wrapped__")

    def test_cli_confirm_with_custom_message(self) -> None:
        """Test confirm decorator with custom confirmation message."""

        @cli_confirm_decorator("Do you want to proceed with this operation?")
        def custom_confirm_function() -> str:
            return "operation completed"

        # Test that decorator is applied
        assert hasattr(custom_confirm_function, "__wrapped__")


# =============================================================================
# REAL FUNCTIONALITY TESTS FOR ASYNC COMMAND
# =============================================================================


class TestAsyncCommand(unittest.TestCase):
    """Test async_command decorator with real async execution."""

    def test_async_command_basic_execution(self) -> None:
        """Test async command decorator with basic execution."""

        @async_command
        async def basic_async_command(value: int) -> int:
            await asyncio.sleep(0.001)
            return value * 2

        # async_command converts async to sync, so call it directly
        result = basic_async_command(5)
        assert result == 10

    def test_async_command_exception_handling(self) -> None:
        """Test async command decorator with exception handling."""

        @async_command
        async def failing_async_command() -> None:
            await asyncio.sleep(0.001)
            msg = "Async command failed"
            raise RuntimeError(msg)

        # async_command converts to sync function, so exceptions propagate normally
        with pytest.raises(RuntimeError, match="Async command failed"):
            failing_async_command()

    def test_async_command_return_type_preservation(self) -> None:
        """Test async command decorator preserves return types."""

        @async_command
        async def typed_async_command() -> dict[str, str]:
            await asyncio.sleep(0.001)
            return {"status": "completed", "message": "success"}

        # Call as sync function after decoration
        result = typed_async_command()
        assert isinstance(result, dict)
        assert result["status"] == "completed"
        assert result["message"] == "success"


# =============================================================================
# INTEGRATION TESTS FOR DECORATOR COMBINATIONS
# =============================================================================


class TestDecoratorIntegration(unittest.TestCase):
    """Test combinations of decorators working together."""

    def test_multiple_decorators_stacking(self) -> None:
        """Test multiple decorators applied to same function."""

        @cli_cache_result(ttl=1)
        @cli_measure_time
        @cli_log_execution
        def multi_decorated_function(x: int) -> int:
            time.sleep(0.001)
            return x * 3

        result1 = multi_decorated_function(5)
        result2 = multi_decorated_function(5)  # Should use cache

        assert result1 == 15
        assert result2 == 15

    def test_error_handling_with_retry_integration(self) -> None:
        """Test error handling decorators working with retry logic."""
        attempt_count = 0

        @cli_handle_keyboard_interrupt
        @cli_retry(max_attempts=3, delay=0.001)
        def retry_with_error_handling() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                msg = "Temporary failure"
                raise ConnectionError(msg)
            return "finally_succeeded"

        result = retry_with_error_handling()
        assert result == "finally_succeeded"
        assert attempt_count == 2

    def test_comprehensive_decorator_combination(self) -> None:
        """Test comprehensive combination of all decorator types."""

        @cli_enhanced(measure_time=True, log_execution=True)
        @cli_cache_result(ttl=10)
        @cli_retry(max_attempts=2, delay=0.001)
        def comprehensive_function(data: str) -> FlextResult[str]:
            return FlextResult[str].ok(f"comprehensive_result_{data}")

        result = comprehensive_function("test")

        assert result.is_success
        assert result.value == "comprehensive_result_test"


if __name__ == "__main__":
    unittest.main()
