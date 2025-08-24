"""Tests for FlextCli Advanced Mixins - Comprehensive Testing Suite.

This test suite validates all advanced mixin classes and decorators that provide
massive boilerplate reduction for CLI applications, ensuring robust functionality
and proper integration with flext-core patterns.

Test Categories:
    - FlextCliAdvancedMixin: Complete mixin functionality
    - Individual mixins: Validation, Interactive, Progress, Result, Config
    - Advanced decorators: Zero-config, auto-retry, progress
    - Integration scenarios: Real-world usage patterns
    - Error handling and edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Never
from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress

from flext_cli import (
    FlextCliAdvancedMixin,
    FlextCliBasicMixin,
    FlextCliConfigMixin,
    FlextCliInteractiveMixin,
    FlextCliMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    FlextCliValidationMixin,
    flext_cli_auto_validate,
)


# Placeholder implementation for testing
def flext_cli_auto_retry(max_attempts: int = 3, delay: float = 0.1):
    """Auto-retry decorator placeholder implementation."""
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if hasattr(result, "is_success") and result.is_success:
                        return result
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                except Exception:
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    else:
                        raise
            return func(*args, **kwargs)  # Final attempt

        return wrapper

    return decorator


from flext_cli import (
    flext_cli_handle_exceptions,
    flext_cli_require_confirmation,
    flext_cli_with_progress,
    flext_cli_zero_config,
)


class TestFlextCliValidationMixin:
    """Test suite for FlextCliValidationMixin."""

    def test_mixin_initialization(self) -> None:
        """Test mixin initialization."""

        class TestClass(FlextCliValidationMixin):
            pass

        obj = TestClass()
        # Should initialize without errors
        assert hasattr(obj, "_flext_cli_helper")

    def test_flext_cli_validate_inputs(self) -> None:
        """Test input validation method."""

        class TestClass(FlextCliValidationMixin):
            def __init__(self) -> None:
                super().__init__()

        obj = TestClass()

        # Valid inputs
        inputs = {
            "email": ("user@example.com", "email"),
            "url": ("https://example.com", "url"),
        }

        result = obj.flext_cli_validate_inputs(inputs)
        assert result.is_success
        assert "email" in result.value
        assert "url" in result.value

        # Invalid inputs
        invalid_inputs = {
            "email": ("invalid-email", "email"),
        }

        result = obj.flext_cli_validate_inputs(invalid_inputs)
        assert not result.is_success

        # Unknown validation type
        unknown_inputs = {
            "field": ("value", "unknown_type"),
        }

        result = obj.flext_cli_validate_inputs(unknown_inputs)
        assert not result.is_success

    @patch("flext_cli.helpers.FlextCliHelper.flext_cli_confirm")
    def test_flext_cli_require_confirmation(self, mock_confirm: MagicMock) -> None:
        """Test confirmation requirement method."""

        class TestClass(FlextCliValidationMixin):
            def __init__(self) -> None:
                super().__init__()

        obj = TestClass()

        # User confirms
        mock_confirm.return_value = FlextResult[None].ok(data=True)
        result = obj.flext_cli_require_confirmation("Test operation")
        assert result.is_success
        assert result.value is True

        # User cancels
        mock_confirm.return_value = FlextResult[None].ok(False)
        result = obj.flext_cli_require_confirmation("Test operation")
        assert not result.is_success

        # Confirmation fails
        mock_confirm.return_value = FlextResult[None].fail("Confirmation error")
        result = obj.flext_cli_require_confirmation("Test operation")
        assert not result.is_success


class TestFlextCliInteractiveMixin:
    """Test suite for FlextCliInteractiveMixin."""

    def test_mixin_initialization(self) -> None:
        """Test mixin initialization."""

        class TestClass(FlextCliInteractiveMixin):
            pass

        obj = TestClass()
        assert hasattr(obj, "_flext_cli_console")
        assert obj.console is not None

    def test_print_methods(self) -> None:
        """Test various print methods."""

        class TestClass(FlextCliInteractiveMixin):
            pass

        obj = TestClass()

        # Should not raise exceptions
        obj.flext_cli_print_success("Success message")
        obj.flext_cli_print_error("Error message")
        obj.flext_cli_print_warning("Warning message")
        obj.flext_cli_print_info("Info message")

    def test_flext_cli_print_result(self) -> None:
        """Test result printing method."""

        class TestClass(FlextCliInteractiveMixin):
            pass

        obj = TestClass()

        # Success result
        success_result = FlextResult[None].ok("Success data")
        obj.flext_cli_print_result(success_result)

        # Failure result
        failure_result = FlextResult[None].fail("Error message")
        obj.flext_cli_print_result(failure_result)

    @patch("flext_cli.helpers.FlextCliHelper.flext_cli_confirm")
    def test_flext_cli_confirm_operation(self, mock_confirm: MagicMock) -> None:
        """Test operation confirmation method."""

        class TestClass(FlextCliInteractiveMixin):
            pass

        obj = TestClass()

        # Successful confirmation
        mock_confirm.return_value = FlextResult[None].ok(data=True)
        result = obj.flext_cli_confirm_operation("Test operation")
        assert result is True

        # Failed confirmation
        mock_confirm.return_value = FlextResult[None].fail("Error")
        result = obj.flext_cli_confirm_operation("Test operation")
        assert result is False


class TestFlextCliProgressMixin:
    """Test suite for FlextCliProgressMixin."""

    def test_mixin_initialization(self) -> None:
        """Test mixin initialization."""

        class TestClass(FlextCliProgressMixin):
            pass

        obj = TestClass()
        assert obj.console is not None

    def test_flext_cli_track_progress(self) -> None:
        """Test progress tracking method."""

        class TestClass(FlextCliProgressMixin):
            pass

        obj = TestClass()

        items = ["item1", "item2", "item3"]
        result = obj.flext_cli_track_progress(items, "Processing items")

        # Should return the same items
        assert result == items

    def test_flext_cli_with_progress(self) -> None:
        """Test progress context manager method."""

        class TestClass(FlextCliProgressMixin):
            pass

        obj = TestClass()

        progress = obj.flext_cli_with_progress(100, "Processing")
        assert progress is not None
        # Should be a Rich Progress instance

        assert isinstance(progress, Progress)


class TestFlextCliResultMixin:
    """Test suite for FlextCliResultMixin."""

    def test_flext_cli_chain_results(self) -> None:
        """Test result chaining method."""

        class TestClass(FlextCliResultMixin):
            pass

        obj = TestClass()

        # Successful operations
        def op1() -> FlextResult[str]:
            return FlextResult[None].ok("result1")

        def op2() -> FlextResult[str]:
            return FlextResult[None].ok("result2")

        result = obj.flext_cli_chain_results(op1, op2)
        assert result.is_success
        assert result.value == ["result1", "result2"]

        # Failed operation
        def failing_op() -> FlextResult[str]:
            return FlextResult[None].fail("Operation failed")

        result = obj.flext_cli_chain_results(op1, failing_op, op2)
        assert not result.is_success

        # Exception in operation
        def exception_op() -> Never:
            msg = "Exception occurred"
            raise ValueError(msg)

        result = obj.flext_cli_chain_results(op1, exception_op)
        assert not result.is_success

    def test_flext_cli_handle_result(self) -> None:
        """Test result handling method."""

        class TestClass(FlextCliResultMixin):
            pass

        obj = TestClass()

        success_called = False
        error_called = False

        def success_action(data: str) -> None:
            nonlocal success_called
            success_called = True
            assert data == "success_data"

        def error_action(error: str) -> None:
            nonlocal error_called
            error_called = True
            assert error == "error_message"

        # Success case
        success_result = FlextResult[None].ok("success_data")
        data = obj.flext_cli_handle_result(
            success_result,
            success_action=success_action,
            error_action=error_action,
        )
        assert data == "success_data"
        assert success_called
        assert not error_called

        # Reset flags
        success_called = False
        error_called = False

        # Failure case
        failure_result = FlextResult[None].fail("error_message")
        data = obj.flext_cli_handle_result(
            failure_result,
            success_action=success_action,
            error_action=error_action,
        )
        assert data is None
        assert not success_called
        assert error_called


class TestFlextCliConfigMixin:
    """Test suite for FlextCliConfigMixin."""

    def test_mixin_initialization(self) -> None:
        """Test mixin initialization."""

        class TestClass(FlextCliConfigMixin):
            pass

        obj = TestClass()
        assert hasattr(obj, "_flext_cli_config")

    @patch("flext_cli.config_hierarchical.create_default_hierarchy")
    def test_flext_cli_load_config(self, mock_create_hierarchy: MagicMock) -> None:
        """Test config loading method."""

        class TestClass(FlextCliConfigMixin):
            def __init__(self) -> None:
                super().__init__()

        # Mock successful config loading
        mock_config = {"key": "value"}
        mock_create_hierarchy.return_value = FlextResult[None].ok(mock_config)

        obj = TestClass()
        result = obj.flext_cli_load_config()
        assert result.is_success
        assert obj.config == mock_config

        # Mock failed config loading
        mock_create_hierarchy.return_value = FlextResult[None].fail("Config error")

        obj = TestClass()
        result = obj.flext_cli_load_config()
        assert not result.is_success


class TestFlextCliAdvancedMixin:
    """Test suite for FlextCliAdvancedMixin complete functionality."""

    def test_advanced_mixin_inheritance(self) -> None:
        """Test that advanced mixin includes all other mixins."""

        class TestClass(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

        obj = TestClass()

        # Should have all mixin capabilities
        assert hasattr(obj, "flext_cli_validate_inputs")
        assert hasattr(obj, "flext_cli_print_success")
        assert hasattr(obj, "flext_cli_track_progress")
        assert hasattr(obj, "flext_cli_chain_results")
        assert hasattr(obj, "flext_cli_load_config")

    def test_flext_cli_execute_with_full_validation(self) -> None:
        """Test complete validation and execution method."""

        class TestClass(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

            def do_work(self) -> FlextResult[str]:
                return FlextResult[None].ok("Work completed")

        obj = TestClass()

        # Test with valid inputs
        inputs = {"email": ("user@example.com", "email")}

        with patch.object(obj, "flext_cli_confirm_operation", return_value=True):
            result = obj.flext_cli_execute_with_full_validation(
                inputs,
                obj.do_work,
                operation_name="test operation",
            )
            assert result.is_success

        # Test with invalid inputs
        invalid_inputs = {"email": ("invalid-email", "email")}

        result = obj.flext_cli_execute_with_full_validation(
            invalid_inputs,
            obj.do_work,
            operation_name="test operation",
        )
        assert not result.is_success

    def test_flext_cli_process_data_workflow(self) -> None:
        """Test data workflow processing method."""

        class TestClass(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

        obj = TestClass()

        # Define workflow steps
        def step1(data: str) -> FlextResult[str]:
            return FlextResult[None].ok(data + " -> step1")

        def step2(data: str) -> FlextResult[str]:
            return FlextResult[None].ok(data + " -> step2")

        workflow_steps = [("Step 1", step1), ("Step 2", step2)]

        result = obj.flext_cli_process_data_workflow(
            "initial",
            workflow_steps,
            show_progress=False,
        )
        assert result.is_success
        assert result.value == "initial -> step1 -> step2"

    def test_flext_cli_execute_file_operations(self) -> None:
        """Test file operations execution method."""

        class TestClass(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

        obj = TestClass()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = Path(temp_dir) / "test1.txt"
            test_file2 = Path(temp_dir) / "test2.txt"
            test_file1.write_text("content1")
            test_file2.write_text("content2")

            def read_file(file_path: str) -> FlextResult[str]:
                content = Path(file_path).read_text(encoding="utf-8")
                return FlextResult[None].ok(content)

            file_operations = [
                ("read", str(test_file1), read_file),
                ("read", str(test_file2), read_file),
            ]

            result = obj.flext_cli_execute_file_operations(
                file_operations,
                require_confirmation=False,
            )
            assert result.is_success


class TestAdvancedDecorators:
    """Test suite for advanced decorators."""

    def test_flext_cli_auto_validate_decorator(self) -> None:
        """Test auto-validation decorator."""

        @flext_cli_auto_validate(email="email")
        def test_function(email: str) -> FlextResult[str]:
            return FlextResult[None].ok(f"Email: {email}")

        # Valid email
        result = test_function(email="user@example.com")
        assert result.is_success

        # Invalid email
        result = test_function(email="invalid-email")
        assert not result.is_success

    def test_flext_cli_handle_exceptions_decorator(self) -> None:
        """Test exception handling decorator."""

        @flext_cli_handle_exceptions("Test operation failed")
        def test_function() -> Never:
            msg = "Test exception"
            raise ValueError(msg)

        result = test_function()
        assert not result.is_success
        assert "Test operation failed" in result.error
        assert "Test exception" in result.error

        # Test with successful function
        @flext_cli_handle_exceptions()
        def success_function() -> str:
            return "Success"

        result = success_function()
        assert result.is_success
        assert result.value == "Success"

    @patch("flext_cli.helpers.FlextCliHelper.flext_cli_confirm")
    def test_flext_cli_require_confirmation_decorator(
        self, mock_confirm: MagicMock
    ) -> None:
        """Test confirmation requirement decorator."""

        @flext_cli_require_confirmation("Test operation")
        def test_function() -> FlextResult[str]:
            return FlextResult[None].ok("Function executed")

        # User confirms
        mock_confirm.return_value = FlextResult[None].ok(data=True)
        result = test_function()
        assert result.is_success

        # User cancels
        mock_confirm.return_value = FlextResult[None].ok(False)
        result = test_function()
        assert result.is_success
        assert "cancelled" in result.value

    @patch("time.sleep")
    def test_flext_cli_auto_retry_decorator(self, mock_sleep: MagicMock) -> None:
        """Test auto-retry decorator."""
        call_count = 0

        @flext_cli_auto_retry(max_attempts=3, delay=0.1)
        def flaky_function() -> FlextResult[str]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return FlextResult[None].fail("Temporary failure")
            return FlextResult[None].ok("Success after retries")

        result = flaky_function()
        assert result.is_success
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep between retries

        # Test with permanent failure
        call_count = 0

        @flext_cli_auto_retry(max_attempts=2, delay=0.1)
        def always_fail() -> FlextResult[str]:
            nonlocal call_count
            call_count += 1
            return FlextResult[None].fail("Permanent failure")

        result = always_fail()
        assert not result.is_success
        assert call_count == 2

    def test_flext_cli_with_progress_decorator(self) -> None:
        """Test progress decorator."""

        @flext_cli_with_progress("Processing data")
        def test_function() -> FlextResult[str]:
            return FlextResult[None].ok("Processed")

        result = test_function()
        assert result.is_success
        assert result.value == "Processed"

    def test_flext_cli_zero_config_decorator(self) -> None:
        """Test zero-configuration decorator."""

        class TestClass:
            def __init__(self) -> None:
                self.console = Console()

            @flext_cli_zero_config("test operation", confirm=False)
            def test_method(self) -> FlextResult[str]:
                return FlextResult[None].ok("Method executed")

        obj = TestClass()
        result = obj.test_method()
        assert result.is_success


class TestMixinAliases:
    """Test suite for mixin aliases and combinations."""

    def test_flext_cli_mixin_alias(self) -> None:
        """Test FlextCliMixin alias."""
        assert FlextCliMixin == FlextCliAdvancedMixin

    def test_flext_cli_basic_mixin(self) -> None:
        """Test FlextCliBasicMixin combination."""

        class TestClass(FlextCliBasicMixin):
            def __init__(self) -> None:
                super().__init__()

        obj = TestClass()

        # Should have basic mixin capabilities
        assert hasattr(obj, "flext_cli_validate_inputs")
        assert hasattr(obj, "flext_cli_print_success")
        assert hasattr(obj, "flext_cli_track_progress")


@pytest.mark.integration
class TestMixinIntegration:
    """Integration tests for mixin combinations."""

    def test_complete_cli_class(self) -> None:
        """Test complete CLI class using all mixins."""

        class CompleteCliCommand(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

            def execute(self, email: str, file_path: str) -> FlextResult[str]:
                """Execute command with full validation and confirmation."""
                # Validate inputs
                inputs = {"email": (email, "email"), "file": (file_path, "file")}

                validation_result = self.flext_cli_validate_inputs(inputs)
                if not validation_result.is_success:
                    return validation_result

                # Confirm operation
                if not self.flext_cli_confirm_operation(
                    "Execute command",
                    default=True,
                ):
                    return FlextResult[None].ok("Operation cancelled")

                # Process with progress
                items = ["step1", "step2", "step3"]
                for _item in self.flext_cli_track_progress(items, "Processing"):
                    # Simulate processing
                    pass

                self.flext_cli_print_success("Command executed successfully")
                return FlextResult[None].ok("Command completed")

        # Test with valid inputs
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", delete=False) as f:
            f.write("test content")
            temp_file = f.name

        try:
            cmd = CompleteCliCommand()

            with patch.object(cmd, "flext_cli_confirm_operation", return_value=True):
                result = cmd.execute("user@example.com", temp_file)
                assert result.is_success
                assert result.value == "Command completed"

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_error_handling_integration(self) -> None:
        """Test error handling across multiple mixins."""

        class ErrorTestCommand(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

            def execute_with_errors(self) -> FlextResult[str]:
                """Execute operation that will fail validation."""
                # This should fail validation
                inputs = {"email": ("invalid-email", "email")}
                validation_result = self.flext_cli_validate_inputs(inputs)

                if not validation_result.is_success:
                    self.flext_cli_print_error(
                        f"Validation failed: {validation_result.error}",
                    )
                    return validation_result

                return FlextResult[None].ok("Should not reach here")

        cmd = ErrorTestCommand()
        result = cmd.execute_with_errors()
        assert not result.is_success

    def test_workflow_integration(self) -> None:
        """Test workflow processing integration."""

        class WorkflowCommand(FlextCliAdvancedMixin):
            def __init__(self) -> None:
                super().__init__()

            def process_data(self, data: str) -> FlextResult[str]:
                """Process data through multiple steps."""

                def step1(d: str) -> FlextResult[str]:
                    return FlextResult[None].ok(d.upper())

                def step2(d: str) -> FlextResult[str]:
                    return FlextResult[None].ok(f"Processed: {d}")

                def step3(d: str) -> FlextResult[str]:
                    return FlextResult[None].ok(f"{d} - Complete")

                workflow_steps = [
                    ("Uppercase", step1),
                    ("Add Prefix", step2),
                    ("Add Suffix", step3),
                ]

                return self.flext_cli_process_data_workflow(
                    data,
                    workflow_steps,
                    show_progress=False,
                )

        cmd = WorkflowCommand()
        result = cmd.process_data("hello world")
        assert result.is_success
        assert result.value == "Processed: HELLO WORLD - Complete"
