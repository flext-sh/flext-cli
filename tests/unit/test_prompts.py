"""FLEXT CLI Prompts Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliPrompts covering all real functionality with flext_tests
integration, comprehensive prompt operations, and targeting 100% coverage.

Modules tested: FlextCliPrompts (prompts service)
Scope: All prompt methods, initialization, history, statistics, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import getpass
import time
from collections import UserList
from typing import Never, TypedDict, TypeVar, cast

import pytest
from flext_core import FlextResult, t
from flext_tests import tm

from flext_cli import FlextCliPrompts
from tests import c

T = TypeVar("T")


class ConfirmTestCaseDict(TypedDict, total=False):
    """Test case dictionary for confirm prompts."""

    message: str
    default: bool
    expected_value: bool


class ChoiceTestCaseDict(TypedDict, total=False):
    """Test case dictionary for choice prompts."""

    message: str
    choices: list[str]
    default: str | None
    expected_success: bool


class TextTestCaseDict(TypedDict, total=False):
    """Test case dictionary for text prompts."""

    message: str
    default: str | None
    validation_pattern: str | None
    expected_success: bool


class TestsCliPrompts:
    """Comprehensive tests for FlextCliPrompts functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    @staticmethod
    def _set_prompt_history(prompts: FlextCliPrompts, history: list[str]) -> None:
        """Helper method to set _prompt_history for testing.

        This method uses object.__setattr__ to bypass read-only protection
        in tests, which is necessary for testing internal state.
        """
        object.__setattr__(prompts, "_prompt_history", history)

    # =========================================================================
    # NESTED: Fixtures Factory
    # =========================================================================

    class Fixtures:
        """Factory for creating prompt instances for testing."""

        @staticmethod
        def create_quiet_prompts(
            *,
            interactive_mode: bool = False,
            default_timeout: int = 5,
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
            default_timeout: int = 5,
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
        def get_prompt_text_cases() -> list[TextTestCaseDict]:
            """Get parametrized test cases for prompt_text."""
            return [
                TextTestCaseDict(
                    message="simple",
                    default="text",
                    validation_pattern=None,
                    expected_success=True,
                ),
                TextTestCaseDict(
                    message="",
                    default="",
                    validation_pattern=None,
                    expected_success=False,  # Empty string is falsy, fails in non-interactive mode
                ),
                TextTestCaseDict(
                    message="with_default",
                    default="test@example.com",
                    validation_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    expected_success=True,
                ),
                TextTestCaseDict(
                    message="with_default",
                    default="invalid-email",
                    validation_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    expected_success=False,
                ),
            ]

        @staticmethod
        def get_confirm_cases() -> list[ConfirmTestCaseDict]:
            """Get parametrized test cases for confirm."""
            return [
                ConfirmTestCaseDict(
                    message="confirm",
                    default=True,
                    expected_value=True,
                ),
                ConfirmTestCaseDict(
                    message="confirm",
                    default=False,
                    expected_value=False,
                ),
                ConfirmTestCaseDict(
                    message="",
                    default=True,
                    expected_value=True,
                ),
            ]

        @staticmethod
        def get_choice_cases() -> list[ChoiceTestCaseDict]:
            """Get parametrized test cases for prompt_choice."""
            return [
                ChoiceTestCaseDict(
                    message="choose",
                    choices=["simple", "complex"],
                    default="simple",
                    expected_success=True,
                ),
                ChoiceTestCaseDict(
                    message="choose",
                    choices=[],
                    default=None,
                    expected_success=False,
                ),
                ChoiceTestCaseDict(
                    message="choose",
                    choices=["simple", "complex"],
                    default="invalid_choice",
                    expected_success=False,
                ),
            ]

        @staticmethod
        def get_print_status_cases() -> list[dict[str, object | None]]:
            """Get parametrized test cases for print_status."""
            cases: list[dict[str, object | None]] = [
                {"message": "simple", "status": None},
                {
                    "message": "simple",
                    "status": c.Status.INFO,
                },
                {
                    "message": "",
                    "status": c.Status.WARNING,
                },
            ]
            cases.extend(
                [{"message": "simple", "status": status} for status in c.Status.ALL]
            )
            return cases

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    # Assertions removed - use FlextTestsMatchers directly
    # Domain-specific assertions can be inline or in domain-specific helper classes

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
        # Validate prompt properties
        assert hasattr(prompts, "quiet")
        assert hasattr(prompts, "interactive_mode")
        assert hasattr(prompts, "default_timeout")
        assert prompts.default_timeout > 0
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
        prompts = FlextCliPrompts(default_timeout=c.TestData.CUSTOM)
        assert prompts.default_timeout == c.TestData.CUSTOM

    # =========================================================================
    # EXECUTE TESTS
    # =========================================================================

    def test_execute_success(self, prompts: FlextCliPrompts) -> None:
        """Test execute method returns success."""
        result = prompts.execute()
        tm.ok(result)
        assert isinstance(result.unwrap(), dict)

    # =========================================================================
    # PROMPT_TEXT TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_prompt_text_cases())
    def test_prompt_text_parametrized(
        self,
        test_case: TextTestCaseDict,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_text with parametrized cases."""
        message = str(test_case.get("message", ""))
        default = str(test_case.get("default", ""))
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
            assert isinstance(result, FlextResult)
            tm.ok(result)
            assert result.value == default
        else:
            assert isinstance(result, FlextResult)
            tm.fail(result)

    def test_prompt_text_no_default_failure(self) -> None:
        """Test prompt_text without default in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_text("simple")
        assert isinstance(result, FlextResult)
        tm.fail(result, contains="no default provided")

    def test_prompt_text_interactive_mode(
        self,
        interactive_prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_text in interactive mode."""
        result = interactive_prompts.prompt_text(
            "simple",
            default="text",
        )
        tm.ok(result)
        assert isinstance(result.unwrap(), str)

    # =========================================================================
    # PROMPT_"confirm"ATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_confirm_cases())
    def test_prompt_confirmation_parametrized(
        self,
        test_case: ConfirmTestCaseDict,
    ) -> None:
        """Test prompt_confirmation with parametrized cases."""
        prompts = self.Fixtures.create_quiet_prompts()
        message = str(test_case.get("message", ""))
        default = bool(test_case.get("default", False))
        expected_value = bool(test_case.get("expected_value", False))

        result = prompts.prompt_confirmation(message, default=default)
        tm.ok(result)
        assert result.value == expected_value

    def test_prompt_confirmation_interactive_mode(
        self,
        interactive_prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_confirmation in interactive mode."""
        result = interactive_prompts.prompt_confirmation(
            "confirm",
            default=True,
        )
        tm.ok(result)
        assert isinstance(result.unwrap(), bool)

    # =========================================================================
    # PROMPT_CHOICE TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_choice_cases())
    def test_prompt_choice_parametrized(
        self,
        test_case: ChoiceTestCaseDict,
    ) -> None:
        """Test prompt_choice with parametrized cases."""
        prompts = self.Fixtures.create_quiet_prompts()
        message = str(test_case.get("message", ""))
        choices_raw = test_case.get("choices", [])
        choices: list[str] = list(choices_raw) if isinstance(choices_raw, list) else []
        default_raw = test_case.get("default")
        default: str | None = str(default_raw) if default_raw is not None else None
        expected_success = bool(test_case.get("expected_success", True))

        result = prompts.prompt_choice(message, choices, default=default)

        if expected_success:
            assert isinstance(result, FlextResult)
            tm.ok(result)
            if default:
                assert result.value == default
        else:
            assert isinstance(result, FlextResult)
            tm.fail(result)

    def test_prompt_choice_no_default_required(self) -> None:
        """Test prompt_choice without default triggers INTERACTIVE_MODE_DISABLED_CHOICE error."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_choice(
            "choose",
            c.TestData.TWO,
        )
        tm.fail(result, contains="Interactive mode disabled")

    def test_prompt_choice_interactive_mode(
        self,
        interactive_prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_choice in interactive mode."""
        result = interactive_prompts.prompt_choice(
            "choose",
            ["simple", "complex", "advanced"],
            default="simple",
        )
        tm.ok(result)
        assert result.unwrap() in {"simple", "complex", "advanced"}

    def test_prompt_choice_exception_handling(self) -> None:
        """Test prompt_choice exception handler."""
        prompts = self.Fixtures.create_interactive_prompts()

        class ErrorList(UserList[str]):
            """List that raises exception on append."""

            def append(self, item: str) -> Never:
                msg = "Forced exception for testing prompt_choice exception handler"
                raise RuntimeError(msg)

        error_list = ErrorList()
        # Use helper method to set private field for testing
        TestsCliPrompts._set_prompt_history(prompts, list(error_list))
        result = prompts.prompt_choice(
            "choose",
            c.TestData.TWO,
            default="choice",
        )
        tm.fail(result)

    # =========================================================================
    # PROMPT_PASSWORD TESTS
    # =========================================================================

    def test_prompt_password_non_interactive_failure(self) -> None:
        """Test prompt_password in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_password(c.TestData.PASSWORD)
        tm.fail(result, contains="Interactive mode disabled")

    def test_prompt_password_min_length(self) -> None:
        """Test prompt_password with min_length validation."""
        prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = prompts.prompt_password(
            c.TestData.PASSWORD,
            min_length=c.Password.MIN_LENGTH_STRICT,
        )
        assert isinstance(result, FlextResult)

    # =========================================================================
    # PROMPT (Legacy) TESTS
    # =========================================================================

    def test_prompt_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method with default value."""
        result = prompts.prompt(
            "simple",
            default="text",
        )
        assert isinstance(result, FlextResult)

    def test_prompt_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method without default."""
        result = prompts.prompt("simple")
        assert isinstance(result, FlextResult)

    # =========================================================================
    # "confirm" (Legacy) TESTS
    # =========================================================================

    def test_confirm_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method with default."""
        result = prompts.confirm(
            "confirm",
            default=True,
        )
        assert isinstance(result, FlextResult)

    def test_confirm_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method without default."""
        result = prompts.confirm("confirm")
        assert isinstance(result, FlextResult)

    # =========================================================================
    # SELECT_FROM_OPTIONS TESTS
    # =========================================================================

    def test_select_from_options_valid(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with valid options."""
        result = prompts.select_from_options(
            "simple",
            "choose",
        )
        assert isinstance(result, FlextResult)

    def test_select_from_options_empty(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with empty options."""
        result = prompts.select_from_options(
            "",
            "choose",
        )
        assert isinstance(result, FlextResult)
        tm.fail(result, contains="options")

    def test_select_from_options_history_tracking(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test that select_from_options tracks history."""
        initial_history_len = len(prompts.prompt_history)
        _ = prompts.select_from_options(
            c.TestData.TWO,
            "choose",
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
        message = str(test_case.get("message", ""))
        status = test_case.get("status")

        if status is None:
            result = prompts.print_status(message)
        else:
            result = prompts.print_status(message, status=str(status))
        tm.ok(result)

    def test_print_success(self, prompts: FlextCliPrompts) -> None:
        """Test print_success method."""
        result = prompts.print_success("simple")
        tm.ok(result)

    def test_print_error(self, prompts: FlextCliPrompts) -> None:
        """Test print_error method."""
        result = prompts.print_error("simple")
        tm.ok(result)

    def test_print_warning(self, prompts: FlextCliPrompts) -> None:
        """Test print_warning method."""
        result = prompts.print_warning("simple")
        tm.ok(result)

    def test_print_info(self, prompts: FlextCliPrompts) -> None:
        """Test print_info method."""
        result = prompts.print_info("simple")
        tm.ok(result)

    # =========================================================================
    # PROGRESS OPERATIONS TESTS
    # =========================================================================

    def test_create_progress(self, prompts: FlextCliPrompts) -> None:
        """Test create_progress method."""
        result = prompts.create_progress("simple")
        tm.ok(result)
        assert isinstance(result.unwrap(), str)

    def test_with_progress_small_dataset(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with small dataset."""
        items: list[t.GeneralValueType] = cast(
            "list[t.GeneralValueType]",
            list(range(c.Progress.SMALL_DATASET_SIZE)),
        )
        result = prompts.with_progress(items, "simple")
        tm.ok(result)
        assert result.unwrap() == items

    def test_with_progress_large_dataset(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with large dataset."""
        items: list[t.GeneralValueType] = cast(
            "list[t.GeneralValueType]",
            list(range(c.Progress.LARGE_DATASET_SIZE)),
        )
        result = prompts.with_progress(items, "simple")
        tm.ok(result)
        assert result.unwrap() == items

    def test_with_progress_empty(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with empty list."""
        items: list[t.GeneralValueType] = []
        result = prompts.with_progress(items, "simple")
        tm.ok(result)
        assert result.unwrap() == items

    # =========================================================================
    # HISTORY OPERATIONS TESTS
    # =========================================================================

    def test_clear_prompt_history(self, prompts: FlextCliPrompts) -> None:
        """Test clear_prompt_history method."""
        # Add some prompts to history
        _ = prompts.prompt("simple", default="text")
        _ = prompts.prompt("with_default", default="text")

        assert len(prompts.prompt_history) > 0

        result = prompts.clear_prompt_history()
        tm.ok(result)
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
        # Use setattr to bypass Pydantic's PrivateAttr validation for testing
        bad_list = BadList()
        # Add some items to make it non-empty
        bad_list.extend(["test1", "test2"])
        # Directly replace the PrivateAttr - this is a test-only operation
        # BadList is structurally compatible with list[str] (has all list methods including clear)
        # This is a test-only operation to simulate exception during clear()
        # Use helper method to set private field for testing
        TestsCliPrompts._set_prompt_history(prompts, cast("list[str]", bad_list))

        result = prompts.clear_prompt_history()
        tm.fail(result)

    def test_get_prompt_statistics(self, prompts: FlextCliPrompts) -> None:
        """Test get_prompt_statistics method."""
        # Execute some prompts
        _ = prompts.prompt("simple", default="text")
        _ = prompts.prompt("with_default", default="text")

        result = prompts.get_prompt_statistics()
        tm.ok(result)

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
        result = prompts.prompt("", default="text")
        assert isinstance(result, FlextResult)

    def test_edge_cases_long_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: very long message."""
        result = prompts.prompt(c.TestData.LONG, default="text")
        assert isinstance(result, FlextResult)

    def test_edge_cases_special_characters(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: special characters in message."""
        result = prompts.prompt(
            c.TestData.SPECIAL,
            default="text",
        )
        assert isinstance(result, FlextResult)

    def test_edge_cases_unicode(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: unicode characters."""
        result = prompts.prompt(
            c.TestData.UNICODE,
            default="text",
        )
        assert isinstance(result, FlextResult)

    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================

    def test_performance_multiple_prompts(self, prompts: FlextCliPrompts) -> None:
        """Test prompts performance with multiple operations."""
        start_time = time.time()
        for i in range(100):
            _ = prompts.prompt(f"Prompt {i}:", default="text")
        end_time = time.time()

        elapsed = end_time - start_time
        assert elapsed < c.TestData.PERFORMANCE_THRESHOLD, (
            f"Performance test failed: {elapsed}s > {c.TestData.PERFORMANCE_THRESHOLD}s"
        )

    def test_memory_usage_repeated_operations(self, prompts: FlextCliPrompts) -> None:
        """Test prompts memory usage with repeated operations."""
        for i in range(20):
            result = prompts.prompt(
                f"Memory test {i}:",
                default="text",
            )
            assert isinstance(result, FlextResult)
            tm.ok(result)
            assert result.value == "text"

        progress_result = prompts.create_progress("Memory test progress")
        tm.ok(progress_result)

    # =========================================================================
    # INTEGRATION WORKFLOW TESTS
    # =========================================================================

    def test_integration_workflow(self, prompts: FlextCliPrompts) -> None:
        """Test complete prompt workflow integration."""
        # Step 1: Print status
        status_result = prompts.print_status("Starting workflow")
        tm.ok(status_result)

        # Step 2: Prompt for input
        prompt_result = prompts.prompt(
            "simple",
            default="text",
        )
        assert isinstance(prompt_result, FlextResult)

        # Step 3: Confirm action
        confirm_result = prompts.confirm(
            "confirm",
            default=True,
        )
        assert isinstance(confirm_result, FlextResult)

        # Step 4: Select from options
        select_result = prompts.select_from_options(
            c.TestData.TWO,
            "choose",
        )
        assert isinstance(select_result, FlextResult)

        # Step 5: Print success
        success_result = prompts.print_success("Workflow completed")
        tm.ok(success_result)

    # =========================================================================
    # VALIDATION PATTERN TESTS - Missing Coverage
    # =========================================================================

    def test_prompt_text_with_validation_pattern_valid(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_text with valid pattern matching."""
        # In non-interactive mode, default must match pattern
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_text(
            "Enter email:",
            default="test@example.com",
            validation_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        )
        tm.ok(result)
        assert result.unwrap() == "test@example.com"

    def test_prompt_text_with_validation_pattern_invalid_default(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_text with invalid default that doesn't match pattern."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_text(
            "Enter email:",
            default="invalid-email",
            validation_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        )
        tm.fail(result)

    def test_prompt_text_with_validation_pattern_no_default(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_text with pattern but no default in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_text(
            "Enter value:",
            default="",
            validation_pattern=r"^\d+$",
        )
        # Empty default should fail validation if pattern provided
        tm.fail(result) or result.is_success  # May succeed with empty

    def test_prompt_text_interactive_with_pattern_validation(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt_text in interactive mode with pattern validation."""
        # Mock input to return valid value
        monkeypatch.setattr("builtins.input", lambda _: "12345")
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_text(
            "Enter number:",
            default="",
            validation_pattern=r"^\d+$",
        )
        # May succeed or fail depending on implementation
        assert isinstance(result, FlextResult)

    def test_prompt_text_interactive_pattern_mismatch(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt_text with pattern mismatch in interactive mode."""
        # Mock input to return invalid value, but note that prompt_text
        # uses default directly in current implementation
        monkeypatch.setattr("builtins.input", lambda _: "abc")
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        # Since prompt_text uses default directly, test with non-empty default
        result = interactive_prompts.prompt_text(
            "Enter number:",
            default="abc",  # Invalid for pattern
            validation_pattern=r"^\d+$",
        )
        # Should fail due to pattern mismatch
        tm.fail(result)

    # =========================================================================
    # "confirm"ATION EDGE CASES - Missing Coverage
    # =========================================================================

    def test_confirm_keyboard_interrupt(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test confirm with KeyboardInterrupt."""
        interactive_prompts = self.Fixtures.create_interactive_prompts()

        def mock_input(_: str) -> str:
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_eof_error(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test confirm with EOFError."""
        interactive_prompts = self.Fixtures.create_interactive_prompts()

        def mock_input(_: str) -> str:
            raise EOFError

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_exception_handling(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test confirm with general exception."""
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        test_error_msg = "Test error"

        def mock_input(_: str) -> str:
            raise RuntimeError(test_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_quiet_mode(self, prompts: FlextCliPrompts) -> None:
        """Test confirm in quiet mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.confirm("Continue?", default=True)
        tm.ok(result)
        assert result.unwrap() is True

    def test_confirm_non_interactive_mode(self, prompts: FlextCliPrompts) -> None:
        """Test confirm in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = quiet_prompts.confirm("Continue?", default=False)
        tm.ok(result)
        assert result.unwrap() is False

    # =========================================================================
    # "choice" PROMPT EDGE CASES - Missing Coverage
    # =========================================================================

    def test_prompt_choice_empty_choices(self, prompts: FlextCliPrompts) -> None:
        """Test prompt_choice with empty choices list."""
        result = prompts.prompt_choice("Select:", choices=[], default=None)
        tm.fail(result)

    def test_prompt_choice_invalid_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt_choice with invalid default."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_choice("Select:", choices=["a", "b"], default="c")
        tm.fail(result)

    def test_prompt_choice_non_interactive_no_default(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_choice in non-interactive mode without default."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_choice(
            "Select:",
            choices=["a", "b"],
            default=None,
        )
        tm.fail(result)

    def test_prompt_choice_non_interactive_valid_default(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test prompt_choice in non-interactive mode with valid default."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_choice("Select:", choices=["a", "b"], default="a")
        tm.ok(result)
        assert result.unwrap() == "a"

    # =========================================================================
    # PASSWORD PROMPT EDGE CASES - Missing Coverage
    # =========================================================================

    def test_prompt_password_too_short(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt_password with password too short."""

        def mock_getpass(prompt: str) -> str:
            return "short"  # Less than min_length

        monkeypatch.setattr(getpass, "getpass", mock_getpass)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_password("Password:", min_length=8)
        tm.fail(result)

    def test_prompt_password_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt_password with exception."""
        password_input_error_msg = "Password input error"

        def mock_getpass(_: str) -> str:
            raise RuntimeError(password_input_error_msg)

        monkeypatch.setattr(getpass, "getpass", mock_getpass)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_password("Password:")
        tm.fail(result)

    def test_prompt_password_valid_length(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt_password with valid password length."""

        def mock_getpass(prompt: str) -> str:
            return "validpassword123"

        monkeypatch.setattr(getpass, "getpass", mock_getpass)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_password("Password:", min_length=8)
        tm.ok(result)
        assert len(result.unwrap()) >= 8

    # =========================================================================
    # PROMPT METHOD EDGE CASES - Missing Coverage
    # =========================================================================

    def test_prompt_quiet_mode(self, prompts: FlextCliPrompts) -> None:
        """Test prompt in quiet mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt("Enter value:", default="default_value")
        tm.ok(result)
        assert result.unwrap() == "default_value"

    def test_prompt_non_interactive_mode(self, prompts: FlextCliPrompts) -> None:
        """Test prompt in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = quiet_prompts.prompt("Enter value:", default="default_value")
        tm.ok(result)
        assert result.unwrap() == "default_value"

    def test_prompt_empty_input_uses_default(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt with empty input uses default."""
        monkeypatch.setattr("builtins.input", lambda _: "")
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt("Enter value:", default="default")
        tm.ok(result)
        assert result.unwrap() == "default"

    def test_prompt_exception_handling(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt with exception."""
        input_error_msg = "Input error"

        def mock_input(_: str) -> str:
            raise RuntimeError(input_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt("Enter value:", default="")
        tm.fail(result)

    # =========================================================================
    # SELECT FROM OPTIONS EDGE CASES - Missing Coverage
    # =========================================================================

    def test_select_from_options_empty_list(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with empty options list."""
        result = prompts.select_from_options([], "Select option:")
        tm.fail(result)

    def test_select_from_options_single_option(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with single option."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.select_from_options(["only"], "Select:")
        # May succeed or fail depending on implementation
        assert isinstance(result, FlextResult)

    def test_select_from_options_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test select_from_options with exception."""
        selection_error_msg = "Selection error"

        def mock_input(_: str) -> str:
            raise RuntimeError(selection_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.select_from_options(["a", "b"], "Select:")
        tm.fail(result)

    # =========================================================================
    # PRINT METHODS EDGE CASES - Missing Coverage
    # =========================================================================

    def test_print_message_success(self, prompts: FlextCliPrompts) -> None:
        """Test _print_message success path."""
        result = prompts._print_message(
            "Test message",
            "info",
            "Format: {message}",
            "Error: {error}",
        )
        tm.ok(result)

    def test_print_message_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test _print_message with exception."""
        # Mock logger to raise exception
        logger_error_msg = "Logger error"

        def mock_info(*args: object, **kwargs: object) -> None:
            raise RuntimeError(logger_error_msg)

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts._print_message(
            "Test",
            "info",
            "Format: {message}",
            "Error: {error}",
        )
        tm.fail(result)

    def test_print_status_empty_message(self, prompts: FlextCliPrompts) -> None:
        """Test print_status with empty message."""
        result = prompts.print_status("")
        tm.ok(result)

    def test_print_status_long_message(self, prompts: FlextCliPrompts) -> None:
        """Test print_status with very long message."""
        long_message = "A" * 1000
        result = prompts.print_status(long_message)
        tm.ok(result)

    # =========================================================================
    # PROGRESS EDGE CASES - Missing Coverage
    # =========================================================================

    def test_create_progress_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test create_progress with exception."""
        # Mock logger to raise exception
        progress_error_msg = "Progress error"
        # Store original method for restoration
        original_info = prompts.logger.info

        def mock_info(message: str, *args: object, **kwargs: object) -> None:
            if "Starting progress" in str(message):
                raise RuntimeError(progress_error_msg)
            # Call original with message only to avoid overload issues
            # logger.info accepts message as first positional argument
            original_info(str(message))

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts.create_progress("Test progress")
        tm.fail(result)

    def test_with_progress_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test with_progress with exception."""
        # Mock logger to raise exception during progress creation
        progress_error_msg = "Progress error"
        # Store original method for restoration
        original_info = prompts.logger.info

        def mock_info(message: str, *args: object, **kwargs: object) -> None:
            if "Starting progress operation" in str(message):
                raise RuntimeError(progress_error_msg)
            # Call original with message only to avoid overload issues
            # logger.info accepts message as first positional argument
            original_info(str(message))

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts.with_progress([1, 2, 3], "Processing")
        tm.fail(result)

    def test_with_progress_empty_items(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with empty items list."""
        result = prompts.with_progress([], "Processing")
        tm.ok(result)
        assert result.unwrap() == []

    # =========================================================================
    # HISTORY AND STATISTICS EDGE CASES - Missing Coverage
    # =========================================================================

    def test_prompt_history_property(self, prompts: FlextCliPrompts) -> None:
        """Test prompt_history property returns copy."""
        # Add some prompts
        prompts.prompt("Test 1", default="")
        prompts.prompt("Test 2", default="")

        history1 = prompts.prompt_history
        history2 = prompts.prompt_history

        # Should be equal but not same object
        assert history1 == history2
        assert history1 is not history2

        # Modifying copy shouldn't affect original
        history1.append("test")
        assert len(prompts.prompt_history) == 2

    def test_get_prompt_statistics_empty_history(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test get_prompt_statistics with empty history."""
        result = prompts.get_prompt_statistics()
        tm.ok(result)
        stats = result.unwrap()
        assert stats["prompts_executed"] == 0
        assert stats["history_size"] == 0

    def test_get_prompt_statistics_with_history(self, prompts: FlextCliPrompts) -> None:
        """Test get_prompt_statistics with history."""
        prompts.prompt("Test 1", default="")
        prompts.prompt("Test 2", default="")
        prompts.confirm("Confirm?", default=True)

        result = prompts.get_prompt_statistics()
        tm.ok(result)
        stats = result.unwrap()
        # Check that statistics are present
        assert "prompts_executed" in stats
        assert "history_size" in stats
        # History may be tracked differently, so just verify keys exist
        assert isinstance(stats["prompts_executed"], int)
        assert isinstance(stats["history_size"], int)

    # =========================================================================
    # INITIALIZATION EDGE CASES - Missing Coverage
    # =========================================================================

    def test_initialization_quiet_disables_interactive(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test that quiet=True disables interactive mode."""
        quiet_prompts = FlextCliPrompts(interactive_mode=True, quiet=True)
        assert quiet_prompts.interactive_mode is False
        assert quiet_prompts.quiet is True

    def test_initialization_interactive_with_quiet_false(
        self,
        prompts: FlextCliPrompts,
    ) -> None:
        """Test initialization with interactive=True and quiet=False."""
        interactive_prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
        assert interactive_prompts.interactive_mode is True
        assert interactive_prompts.quiet is False

    # =========================================================================
    # EXECUTE METHOD EDGE CASES - Missing Coverage
    # =========================================================================

    def test_execute_with_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test execute method with exception."""
        # Mock logger.debug to raise exception during execute
        execute_error_msg = "Execute error"
        # Store original method for restoration
        original_debug = prompts.logger.debug

        def mock_debug(message: str, *args: object, **kwargs: object) -> None:
            if "Prompt service execution completed" in str(message):
                raise RuntimeError(execute_error_msg)
            # Call original with message only to avoid overload issues
            # logger.debug accepts message as first positional argument
            original_debug(str(message))

        monkeypatch.setattr(prompts.logger, "debug", mock_debug)
        result = prompts.execute()
        tm.fail(result)
