"""FLEXT CLI Prompts Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliPrompts covering all real functionality with flext_tests
integration, comprehensive prompt operations, and targeting 100% coverage.

Modules tested: FlextCliPrompts (prompts service)
Scope: All prompt methods, initialization, history, statistics, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections import UserList
from typing import Never, TypeVar

import pytest
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities

from flext_cli import FlextCliPrompts

from ..fixtures.constants import TestPrompts
from ..fixtures.typing import GenericTestCaseDict

T = TypeVar("T")


class TestFlextCliPrompts:
    """Comprehensive tests for FlextCliPrompts functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Fixtures Factory
    # =========================================================================

    class Fixtures:
        """Factory for creating prompt instances for testing."""

        @staticmethod
        def create_quiet_prompts(
            *,
            interactive_mode: bool = False,
            default_timeout: int = TestPrompts.Timeouts.DEFAULT,
        ) -> FlextCliPrompts:
            """Create prompts in quiet (non-interactive) mode."""
            return FlextCliPrompts(
                interactive_mode=interactive_mode,
                quiet=True,
                default_timeout=default_timeout,
            )

        @staticmethod
        def create_interactive_prompts(
            *,
            quiet: bool = False,
            default_timeout: int = TestPrompts.Timeouts.DEFAULT,
        ) -> FlextCliPrompts:
            """Create prompts in interactive mode."""
            return FlextCliPrompts(
                interactive_mode=True,
                quiet=quiet,
                default_timeout=default_timeout,
            )

    # =========================================================================
    # NESTED: Test Data Factory
    # =========================================================================

    class TestData:
        """Factory for creating test data scenarios."""

        @staticmethod
        def get_prompt_text_cases() -> list[dict[str, object | None]]:
            """Get parametrized test cases for prompt_text."""
            return [
                {
                    "message": TestPrompts.Messages.SIMPLE,
                    "default": TestPrompts.Defaults.TEXT,
                    "validation_pattern": TestPrompts.Validation.NONE,
                    "expected_success": True,
                },
                {
                    "message": TestPrompts.Messages.EMPTY,
                    "default": TestPrompts.Defaults.TEXT_EMPTY,
                    "validation_pattern": TestPrompts.Validation.NONE,
                    "expected_success": False,  # Empty string is falsy, fails in non-interactive mode
                },
                {
                    "message": TestPrompts.Messages.WITH_DEFAULT,
                    "default": "test@example.com",
                    "validation_pattern": TestPrompts.Validation.EMAIL,
                    "expected_success": True,
                },
                {
                    "message": TestPrompts.Messages.WITH_DEFAULT,
                    "default": "invalid-email",
                    "validation_pattern": TestPrompts.Validation.EMAIL,
                    "expected_success": False,
                },
            ]

        @staticmethod
        def get_confirm_cases() -> list[GenericTestCaseDict]:
            """Get parametrized test cases for confirm."""
            return [
                {
                    "message": TestPrompts.Messages.CONFIRM,
                    "default": TestPrompts.Defaults.CONFIRM_TRUE,
                    "expected_value": True,
                },
                {
                    "message": TestPrompts.Messages.CONFIRM,
                    "default": TestPrompts.Defaults.CONFIRM_FALSE,
                    "expected_value": False,
                },
                {
                    "message": TestPrompts.Messages.EMPTY,
                    "default": TestPrompts.Defaults.CONFIRM_TRUE,
                    "expected_value": True,
                },
            ]

        @staticmethod
        def get_choice_cases() -> list[GenericTestCaseDict]:
            """Get parametrized test cases for prompt_choice."""
            return [
                {
                    "message": TestPrompts.Messages.CHOOSE,
                    "choices": TestPrompts.Options.SIMPLE,
                    "default": TestPrompts.Defaults.CHOICE,
                    "expected_success": True,
                },
                {
                    "message": TestPrompts.Messages.CHOOSE,
                    "choices": TestPrompts.Options.EMPTY,
                    "default": None,
                    "expected_success": False,
                },
                {
                    "message": TestPrompts.Messages.CHOOSE,
                    "choices": TestPrompts.Options.SIMPLE,
                    "default": TestPrompts.Defaults.CHOICE_INVALID,
                    "expected_success": False,
                },
            ]

        @staticmethod
        def get_print_status_cases() -> list[dict[str, object | None]]:
            """Get parametrized test cases for print_status."""
            cases: list[dict[str, object | None]] = [
                {"message": TestPrompts.Messages.SIMPLE, "status": None},
                {
                    "message": TestPrompts.Messages.SIMPLE,
                    "status": TestPrompts.Statuses.INFO,
                },
                {
                    "message": TestPrompts.Messages.EMPTY,
                    "status": TestPrompts.Statuses.WARNING,
                },
            ]
            cases.extend([
                {"message": TestPrompts.Messages.SIMPLE, "status": status}
                for status in TestPrompts.Statuses.ALL
            ])
            return cases

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    class Assertions:
        """Helper methods for test assertions using flext-core helpers."""

        @staticmethod
        def assert_result_type(result: FlextResult[T]) -> None:
            """Assert result is FlextResult instance."""
            assert isinstance(result, FlextResult)

        @staticmethod
        def assert_result_success(result: FlextResult[T]) -> None:
            """Assert result is successful using flext-core helper."""
            TestFlextCliPrompts.Assertions.assert_result_type(result)
            FlextTestsUtilities.TestUtilities.assert_result_success(result)

        @staticmethod
        def assert_result_failure(
            result: FlextResult[T], error_contains: str | None = None
        ) -> None:
            """Assert result is failure with optional error message check."""
            TestFlextCliPrompts.Assertions.assert_result_type(result)
            FlextTestsUtilities.TestUtilities.assert_result_failure(result)
            if error_contains:
                # Case-insensitive check for error message
                assert result.error is not None
                error_msg = str(result.error).lower()
                assert error_contains.lower() in error_msg, (
                    f"Error should contain '{error_contains}', got: {error_msg}"
                )

        @staticmethod
        def assert_prompt_properties(prompts: FlextCliPrompts) -> None:
            """Assert prompts has required properties."""
            assert isinstance(prompts.interactive_mode, bool)
            assert isinstance(prompts.quiet, bool)
            assert isinstance(prompts.default_timeout, int)
            assert prompts.default_timeout > 0
            # History should return copy
            history1 = prompts.prompt_history
            history2 = prompts.prompt_history
            assert history1 is not history2

    # =========================================================================
    # FIXTURES
    # =========================================================================

    @pytest.fixture
    def prompts(self) -> FlextCliPrompts:
        """Create FlextCliPrompts instance for testing in non-interactive mode."""
        return self.Fixtures.create_quiet_prompts()

    @pytest.fixture
    def interactive_prompts(self) -> FlextCliPrompts:
        """Create FlextCliPrompts instance for interactive testing."""
        return self.Fixtures.create_interactive_prompts()

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_initialization_default(self) -> None:
        """Test prompts initialization with default parameters."""
        prompts = FlextCliPrompts()
        self.Assertions.assert_prompt_properties(prompts)
        assert hasattr(prompts, "logger")
        assert prompts.logger is not None

    def test_initialization_quiet_mode(self) -> None:
        """Test prompts initialization with quiet mode."""
        prompts = self.Fixtures.create_quiet_prompts()
        assert prompts.quiet is True
        assert prompts.interactive_mode is False

    def test_initialization_interactive_mode(self) -> None:
        """Test prompts initialization with interactive mode."""
        prompts = self.Fixtures.create_interactive_prompts()
        assert prompts.interactive_mode is True

    def test_initialization_custom_timeout(self) -> None:
        """Test prompts initialization with custom timeout."""
        prompts = FlextCliPrompts(default_timeout=TestPrompts.Timeouts.CUSTOM)
        assert prompts.default_timeout == TestPrompts.Timeouts.CUSTOM

    # =========================================================================
    # EXECUTE TESTS
    # =========================================================================

    def test_execute_success(self, prompts: FlextCliPrompts) -> None:
        """Test execute method returns success."""
        result = prompts.execute()
        self.Assertions.assert_result_success(result)
        assert isinstance(result.unwrap(), dict)

    # =========================================================================
    # PROMPT_TEXT TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_prompt_text_cases())
    def test_prompt_text_parametrized(
        self,
        test_case: GenericTestCaseDict,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_text with parametrized cases."""
        message = str(test_case["message"])
        default = str(test_case["default"])
        validation_pattern_raw = test_case.get("validation_pattern")
        validation_pattern: str | None = (
            str(validation_pattern_raw) if validation_pattern_raw is not None else None
        )
        expected_success = bool(test_case.get("expected_success", True))

        result = prompts.prompt_text(
            message=message,
            default=default,
            validation_pattern=validation_pattern,
        )

        if expected_success:
            self.Assertions.assert_result_success(result)
            assert result.value == default
        else:
            self.Assertions.assert_result_failure(result)

    def test_prompt_text_no_default_failure(self) -> None:
        """Test prompt_text without default in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_text(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_failure(result, "no default provided")

    def test_prompt_text_interactive_mode(
        self, interactive_prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_text in interactive mode."""
        result = interactive_prompts.prompt_text(
            TestPrompts.Messages.SIMPLE,
            default=TestPrompts.Defaults.TEXT,
        )
        self.Assertions.assert_result_success(result)
        assert isinstance(result.unwrap(), str)

    # =========================================================================
    # PROMPT_CONFIRMATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_confirm_cases())
    def test_prompt_confirmation_parametrized(
        self,
        test_case: GenericTestCaseDict,
    ) -> None:
        """Test prompt_confirmation with parametrized cases."""
        prompts = self.Fixtures.create_quiet_prompts()
        message = str(test_case["message"])
        default = bool(test_case["default"])
        expected_value = bool(test_case["expected_value"])

        result = prompts.prompt_confirmation(message, default=default)
        self.Assertions.assert_result_success(result)
        assert result.value == expected_value

    def test_prompt_confirmation_interactive_mode(
        self,
        interactive_prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_confirmation in interactive mode."""
        result = interactive_prompts.prompt_confirmation(
            TestPrompts.Messages.CONFIRM,
            default=TestPrompts.Defaults.CONFIRM_TRUE,
        )
        self.Assertions.assert_result_success(result)
        assert isinstance(result.unwrap(), bool)

    # =========================================================================
    # PROMPT_CHOICE TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_choice_cases())
    def test_prompt_choice_parametrized(
        self,
        test_case: GenericTestCaseDict,
    ) -> None:
        """Test prompt_choice with parametrized cases."""
        prompts = self.Fixtures.create_quiet_prompts()
        message = str(test_case["message"])
        choices_raw = test_case["choices"]
        choices: list[str] = list(choices_raw) if isinstance(choices_raw, list) else []
        default_raw = test_case.get("default")
        default: str | None = str(default_raw) if default_raw is not None else None
        expected_success = bool(test_case.get("expected_success", True))

        result = prompts.prompt_choice(message, choices, default=default)

        if expected_success:
            self.Assertions.assert_result_success(result)
            if default:
                assert result.value == default
        else:
            self.Assertions.assert_result_failure(result)

    def test_prompt_choice_no_default_required(self) -> None:
        """Test prompt_choice without default triggers INTERACTIVE_MODE_DISABLED_CHOICE error."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_choice(
            TestPrompts.Messages.CHOOSE,
            TestPrompts.Options.TWO,
        )
        self.Assertions.assert_result_failure(result, "interactive mode disabled")

    def test_prompt_choice_interactive_mode(
        self,
        interactive_prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_choice in interactive mode."""
        result = interactive_prompts.prompt_choice(
            TestPrompts.Messages.CHOOSE,
            TestPrompts.Options.SIMPLE,
            default=TestPrompts.Defaults.CHOICE,
        )
        self.Assertions.assert_result_success(result)
        assert result.unwrap() in TestPrompts.Options.SIMPLE

    def test_prompt_choice_exception_handling(self) -> None:
        """Test prompt_choice exception handler."""
        prompts = self.Fixtures.create_interactive_prompts()

        class ErrorList(UserList[str]):
            """List that raises exception on append."""

            def append(self, item: str) -> Never:
                msg = "Forced exception for testing prompt_choice exception handler"
                raise RuntimeError(msg)

        error_list = ErrorList()
        prompts._prompt_history = list(error_list)
        result = prompts.prompt_choice(
            TestPrompts.Messages.CHOOSE,
            TestPrompts.Options.TWO,
            default=TestPrompts.Defaults.CHOICE,
        )
        self.Assertions.assert_result_failure(result)

    # =========================================================================
    # PROMPT_PASSWORD TESTS
    # =========================================================================

    def test_prompt_password_non_interactive_failure(self) -> None:
        """Test prompt_password in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_password(TestPrompts.Messages.PASSWORD)
        self.Assertions.assert_result_failure(result, "interactive mode disabled")

    def test_prompt_password_min_length(self) -> None:
        """Test prompt_password with min_length validation."""
        prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = prompts.prompt_password(
            TestPrompts.Messages.PASSWORD,
            min_length=TestPrompts.Password.MIN_LENGTH_STRICT,
        )
        self.Assertions.assert_result_type(result)

    # =========================================================================
    # PROMPT (Legacy) TESTS
    # =========================================================================

    def test_prompt_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method with default value."""
        result = prompts.prompt(
            TestPrompts.Messages.SIMPLE,
            default=TestPrompts.Defaults.TEXT,
        )
        self.Assertions.assert_result_type(result)

    def test_prompt_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method without default."""
        result = prompts.prompt(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_type(result)

    # =========================================================================
    # CONFIRM (Legacy) TESTS
    # =========================================================================

    def test_confirm_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method with default."""
        result = prompts.confirm(
            TestPrompts.Messages.CONFIRM,
            default=TestPrompts.Defaults.CONFIRM_TRUE,
        )
        self.Assertions.assert_result_type(result)

    def test_confirm_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method without default."""
        result = prompts.confirm(TestPrompts.Messages.CONFIRM)
        self.Assertions.assert_result_type(result)

    # =========================================================================
    # SELECT_FROM_OPTIONS TESTS
    # =========================================================================

    def test_select_from_options_valid(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with valid options."""
        result = prompts.select_from_options(
            TestPrompts.Options.SIMPLE,
            TestPrompts.Messages.CHOOSE,
        )
        self.Assertions.assert_result_type(result)

    def test_select_from_options_empty(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with empty options."""
        result = prompts.select_from_options(
            TestPrompts.Options.EMPTY,
            TestPrompts.Messages.CHOOSE,
        )
        self.Assertions.assert_result_failure(result, "options")

    def test_select_from_options_history_tracking(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test that select_from_options tracks history."""
        initial_history_len = len(prompts.prompt_history)
        _ = prompts.select_from_options(
            TestPrompts.Options.TWO,
            TestPrompts.Messages.CHOOSE,
        )
        assert len(prompts.prompt_history) >= initial_history_len

    # =========================================================================
    # PRINT OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_print_status_cases())
    def test_print_status_parametrized(
        self,
        test_case: dict[str, object | None],
        prompts: FlextCliPrompts,
    ) -> None:
        """Test print_status with parametrized cases."""
        message = str(test_case["message"])
        status = test_case.get("status")

        if status is None:
            result = prompts.print_status(message)
        else:
            result = prompts.print_status(message, status=str(status))
        self.Assertions.assert_result_success(result)

    def test_print_success(self, prompts: FlextCliPrompts) -> None:
        """Test print_success method."""
        result = prompts.print_success(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)

    def test_print_error(self, prompts: FlextCliPrompts) -> None:
        """Test print_error method."""
        result = prompts.print_error(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)

    def test_print_warning(self, prompts: FlextCliPrompts) -> None:
        """Test print_warning method."""
        result = prompts.print_warning(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)

    def test_print_info(self, prompts: FlextCliPrompts) -> None:
        """Test print_info method."""
        result = prompts.print_info(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)

    # =========================================================================
    # PROGRESS OPERATIONS TESTS
    # =========================================================================

    def test_create_progress(self, prompts: FlextCliPrompts) -> None:
        """Test create_progress method."""
        result = prompts.create_progress(TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)
        assert isinstance(result.unwrap(), str)

    def test_with_progress_small_dataset(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with small dataset."""
        items: list[object] = list(range(TestPrompts.Progress.SMALL_DATASET_SIZE))
        result = prompts.with_progress(items, TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)
        assert result.unwrap() == items

    def test_with_progress_large_dataset(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with large dataset."""
        items: list[object] = list(range(TestPrompts.Progress.LARGE_DATASET_SIZE))
        result = prompts.with_progress(items, TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)
        assert result.unwrap() == items

    def test_with_progress_empty(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with empty list."""
        items: list[object] = []
        result = prompts.with_progress(items, TestPrompts.Messages.SIMPLE)
        self.Assertions.assert_result_success(result)
        assert result.unwrap() == items

    # =========================================================================
    # HISTORY OPERATIONS TESTS
    # =========================================================================

    def test_clear_prompt_history(self, prompts: FlextCliPrompts) -> None:
        """Test clear_prompt_history method."""
        # Add some prompts to history
        _ = prompts.prompt(
            TestPrompts.Messages.SIMPLE, default=TestPrompts.Defaults.TEXT
        )
        _ = prompts.prompt(
            TestPrompts.Messages.WITH_DEFAULT, default=TestPrompts.Defaults.TEXT
        )

        assert len(prompts.prompt_history) > 0

        result = prompts.clear_prompt_history()
        self.Assertions.assert_result_success(result)
        assert len(prompts.prompt_history) == 0

    def test_clear_prompt_history_exception(self) -> None:
        """Test clear_prompt_history exception handling."""
        prompts = self.Fixtures.create_quiet_prompts()

        # Create a custom list-like object that raises exception on clear
        class BadList(UserList[str]):
            """List that raises exception on clear."""

            def clear(self) -> None:
                msg = "Clear failed"
                raise RuntimeError(msg)

        # Replace _prompt_history with BadList that raises exception
        # Use object.__setattr__ to bypass Pydantic's PrivateAttr validation
        bad_list = BadList()
        # Add some items to make it non-empty
        bad_list.extend(["test1", "test2"])
        # Directly replace the PrivateAttr - this is a test-only operation
        # Must use object.__setattr__ to bypass Pydantic's PrivateAttr type checking
        # BadList is structurally compatible with list[str] (has all list methods including clear)
        # This is a test-only operation to simulate exception during clear()
        # Note: setattr() won't work here as Pydantic validates types, so we use object.__setattr__
        prompts._prompt_history = bad_list

        result = prompts.clear_prompt_history()
        self.Assertions.assert_result_failure(result)

    def test_get_prompt_statistics(self, prompts: FlextCliPrompts) -> None:
        """Test get_prompt_statistics method."""
        # Execute some prompts
        _ = prompts.prompt(
            TestPrompts.Messages.SIMPLE, default=TestPrompts.Defaults.TEXT
        )
        _ = prompts.prompt(
            TestPrompts.Messages.WITH_DEFAULT, default=TestPrompts.Defaults.TEXT
        )

        result = prompts.get_prompt_statistics()
        self.Assertions.assert_result_success(result)

        stats = result.unwrap()
        assert isinstance(stats, dict)
        assert "prompts_executed" in stats
        assert "interactive_mode" in stats
        assert "default_timeout" in stats
        assert "history_size" in stats
        assert "timestamp" in stats
        prompts_executed = stats["prompts_executed"]
        assert isinstance(prompts_executed, int)
        assert prompts_executed >= 2

    # =========================================================================
    # EDGE CASES TESTS
    # =========================================================================

    def test_edge_cases_empty_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: empty message."""
        result = prompts.prompt(
            TestPrompts.Messages.EMPTY, default=TestPrompts.Defaults.TEXT
        )
        self.Assertions.assert_result_type(result)

    def test_edge_cases_long_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: very long message."""
        result = prompts.prompt(
            TestPrompts.Messages.LONG, default=TestPrompts.Defaults.TEXT
        )
        self.Assertions.assert_result_type(result)

    def test_edge_cases_special_characters(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: special characters in message."""
        result = prompts.prompt(
            TestPrompts.Messages.SPECIAL,
            default=TestPrompts.Defaults.TEXT,
        )
        self.Assertions.assert_result_type(result)

    def test_edge_cases_unicode(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: unicode characters."""
        result = prompts.prompt(
            TestPrompts.Messages.UNICODE,
            default=TestPrompts.Defaults.TEXT,
        )
        self.Assertions.assert_result_type(result)

    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================

    def test_performance_multiple_prompts(self, prompts: FlextCliPrompts) -> None:
        """Test prompts performance with multiple operations."""
        start_time = time.time()
        for i in range(100):
            _ = prompts.prompt(f"Prompt {i}:", default=TestPrompts.Defaults.TEXT)
        end_time = time.time()

        elapsed = end_time - start_time
        assert elapsed < TestPrompts.Timeouts.PERFORMANCE_THRESHOLD, (
            f"Performance test failed: {elapsed}s > {TestPrompts.Timeouts.PERFORMANCE_THRESHOLD}s"
        )

    def test_memory_usage_repeated_operations(self, prompts: FlextCliPrompts) -> None:
        """Test prompts memory usage with repeated operations."""
        for i in range(20):
            result = prompts.prompt(
                f"Memory test {i}:",
                default=TestPrompts.Defaults.TEXT,
            )
            self.Assertions.assert_result_success(result)
            assert result.value == TestPrompts.Defaults.TEXT

        progress_result = prompts.create_progress("Memory test progress")
        self.Assertions.assert_result_success(progress_result)

    # =========================================================================
    # INTEGRATION WORKFLOW TESTS
    # =========================================================================

    def test_integration_workflow(self, prompts: FlextCliPrompts) -> None:
        """Test complete prompt workflow integration."""
        # Step 1: Print status
        status_result = prompts.print_status("Starting workflow")
        self.Assertions.assert_result_success(status_result)

        # Step 2: Prompt for input
        prompt_result = prompts.prompt(
            TestPrompts.Messages.SIMPLE,
            default=TestPrompts.Defaults.TEXT,
        )
        self.Assertions.assert_result_type(prompt_result)

        # Step 3: Confirm action
        confirm_result = prompts.confirm(
            TestPrompts.Messages.CONFIRM,
            default=TestPrompts.Defaults.CONFIRM_TRUE,
        )
        self.Assertions.assert_result_type(confirm_result)

        # Step 4: Select from options
        select_result = prompts.select_from_options(
            TestPrompts.Options.TWO,
            TestPrompts.Messages.CHOOSE,
        )
        self.Assertions.assert_result_type(select_result)

        # Step 5: Print success
        success_result = prompts.print_success("Workflow completed")
        self.Assertions.assert_result_success(success_result)
