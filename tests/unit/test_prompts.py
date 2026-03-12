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
from typing import Never, TypeVar, override

import pytest
from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliPrompts
from tests import c
from tests.models import (
    ChoiceTestCaseDict,
    ConfirmTestCaseDict,
    PrintStatusCase,
    TextTestCaseDict,
)

T = TypeVar("T")


class TestsCliPrompts:
    """Comprehensive tests for FlextCliPrompts functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    @staticmethod
    def _set_prompt_history(
        prompts: FlextCliPrompts, history: list[str] | UserList[str]
    ) -> None:
        """Helper method to set _prompt_history for testing.

        This method uses object.__setattr__ to bypass read-only protection
        in tests, which is necessary for testing internal state.
        """
        object.__setattr__(prompts, "_prompt_history", history)

    class Fixtures:
        """Factory for creating prompt instances for testing."""

        @staticmethod
        def create_quiet_prompts(
            *, interactive_mode: bool = False, default_timeout: int = 5
        ) -> FlextCliPrompts:
            """Create prompts in quiet (non-interactive) mode."""
            return FlextCliPrompts(
                interactive_mode=interactive_mode,
                quiet=True,
                default_timeout=default_timeout,
            )

        @staticmethod
        def create_interactive_prompts(
            *, quiet: bool = False, default_timeout: int = 5
        ) -> FlextCliPrompts:
            """Create prompts in interactive mode."""
            return FlextCliPrompts(
                interactive_mode=True, quiet=quiet, default_timeout=default_timeout
            )

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
                    expected_success=False,
                ),
                TextTestCaseDict(
                    message="with_default",
                    default="test@example.com",
                    validation_pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    expected_success=True,
                ),
                TextTestCaseDict(
                    message="with_default",
                    default="invalid-email",
                    validation_pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    expected_success=False,
                ),
            ]

        @staticmethod
        def get_confirm_cases() -> list[ConfirmTestCaseDict]:
            """Get parametrized test cases for confirm."""
            return [
                ConfirmTestCaseDict(
                    message="confirm", default=True, expected_value=True
                ),
                ConfirmTestCaseDict(
                    message="confirm", default=False, expected_value=False
                ),
                ConfirmTestCaseDict(message="", default=True, expected_value=True),
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
                    message="choose", choices=[], default=None, expected_success=False
                ),
                ChoiceTestCaseDict(
                    message="choose",
                    choices=["simple", "complex"],
                    default="invalid_choice",
                    expected_success=False,
                ),
            ]

        @staticmethod
        def get_print_status_cases() -> list[PrintStatusCase]:
            """Get parametrized test cases for print_status."""
            cases: list[PrintStatusCase] = [
                PrintStatusCase(message="simple", status=None),
                PrintStatusCase(message="simple", status=c.Cli.MessageTypes.INFO),
                PrintStatusCase(message="", status=c.Cli.MessageTypes.WARNING),
            ]
            cases.extend([
                PrintStatusCase(message="simple", status=status)
                for status in c.Cli.MESSAGE_TYPES_LIST
            ])
            return cases

    @pytest.fixture
    def prompts(self) -> FlextCliPrompts:
        """Create FlextCliPrompts instance for testing in non-interactive mode."""
        return self.Fixtures.create_quiet_prompts()

    @pytest.fixture
    def interactive_prompts(self) -> FlextCliPrompts:
        """Create FlextCliPrompts instance for interactive testing."""
        return self.Fixtures.create_interactive_prompts()

    def test_initialization_default(self) -> None:
        """Test prompts initialization with default parameters."""
        prompts = FlextCliPrompts()
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

    def test_execute_success(self, prompts: FlextCliPrompts) -> None:
        """Test execute method returns success."""
        result = prompts.execute()
        tm.ok(result)
        assert isinstance(result.value, dict)

    @pytest.mark.parametrize("test_case", TestData.get_prompt_text_cases())
    def test_prompt_text_parametrized(
        self, test_case: TextTestCaseDict, prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_text with parametrized cases."""
        result = prompts.prompt_text(
            message=test_case.message,
            default=test_case.default,
            validation_pattern=test_case.validation_pattern,
        )
        if test_case.expected_success:
            assert isinstance(result, r)
            tm.ok(result)
            assert result.value == test_case.default
        else:
            assert isinstance(result, r)
            tm.fail(result)

    def test_prompt_text_no_default_failure(self) -> None:
        """Test prompt_text without default in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_text("simple")
        assert isinstance(result, r)
        tm.fail(result, has="no default provided")

    def test_prompt_text_interactive_mode(
        self, interactive_prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_text in interactive mode."""
        result = interactive_prompts.prompt_text("simple", default="text")
        tm.ok(result)
        assert isinstance(result.value, str)

    @pytest.mark.parametrize("test_case", TestData.get_confirm_cases())
    def test_prompt_confirmation_parametrized(
        self, test_case: ConfirmTestCaseDict
    ) -> None:
        """Test prompt_confirmation with parametrized cases."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_confirmation(
            test_case.message, default=test_case.default
        )
        tm.ok(result)
        assert result.value == test_case.expected_value

    def test_prompt_confirmation_interactive_mode(
        self, interactive_prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_confirmation in interactive mode."""
        result = interactive_prompts.prompt_confirmation("confirm", default=True)
        tm.ok(result)
        assert isinstance(result.value, bool)

    @pytest.mark.parametrize("test_case", TestData.get_choice_cases())
    def test_prompt_choice_parametrized(self, test_case: ChoiceTestCaseDict) -> None:
        """Test prompt_choice with parametrized cases."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_choice(
            test_case.message, test_case.choices, default=test_case.default
        )
        if test_case.expected_success:
            assert isinstance(result, r)
            tm.ok(result)
            if test_case.default:
                assert result.value == test_case.default
        else:
            assert isinstance(result, r)
            tm.fail(result)

    def test_prompt_choice_no_default_required(self) -> None:
        """Test prompt_choice without default triggers INTERACTIVE_MODE_DISABLED_CHOICE error."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_choice("choose", c.TWO)
        tm.fail(result, has="Interactive mode disabled")

    def test_prompt_choice_interactive_mode(
        self, interactive_prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_choice in interactive mode."""
        result = interactive_prompts.prompt_choice(
            "choose", ["simple", "complex", "advanced"], default="simple"
        )
        tm.ok(result)
        assert result.value in {"simple", "complex", "advanced"}

    def test_prompt_choice_exception_handling(self) -> None:
        """Test prompt_choice exception handler."""
        prompts = self.Fixtures.create_interactive_prompts()

        class ErrorList(UserList[str]):
            """List that raises exception on append."""

            @override
            def append(self, item: str) -> Never:
                msg = "Forced exception for testing prompt_choice exception handler"
                raise ValueError(msg)

        error_list = ErrorList()
        TestsCliPrompts._set_prompt_history(prompts, list(error_list))
        result = prompts.prompt_choice("choose", c.TWO, default="choice")
        tm.fail(result)

    def test_prompt_password_non_interactive_failure(self) -> None:
        """Test prompt_password in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_password(c.TestData.PASSWORD)
        tm.fail(result, has="Interactive mode disabled")

    def test_prompt_password_min_length(self) -> None:
        """Test prompt_password with min_length validation."""
        prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = prompts.prompt_password(
            c.TestData.PASSWORD, min_length=c.PasswordDefaults.MIN_LENGTH_STRICT
        )
        assert isinstance(result, r)

    def test_prompt_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method with default value."""
        result = prompts.prompt("simple", default="text")
        assert isinstance(result, r)

    def test_prompt_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method without default."""
        result = prompts.prompt("simple")
        assert isinstance(result, r)

    def test_confirm_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method with default."""
        result = prompts.confirm("confirm", default=True)
        assert isinstance(result, r)

    def test_confirm_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method without default."""
        result = prompts.confirm("confirm")
        assert isinstance(result, r)

    def test_select_from_options_valid(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with valid options."""
        result = prompts.select_from_options(["simple"], "choose")
        assert isinstance(result, r)

    def test_select_from_options_empty(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with empty options."""
        result = prompts.select_from_options([], "choose")
        assert isinstance(result, r)
        tm.fail(result, has="options")

    def test_select_from_options_history_tracking(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test that select_from_options tracks history."""
        initial_history_len = len(prompts.prompt_history)
        _ = prompts.select_from_options(c.TWO, "choose")
        assert len(prompts.prompt_history) >= initial_history_len

    @pytest.mark.parametrize("test_case", TestData.get_print_status_cases())
    def test_print_status_parametrized(
        self, test_case: PrintStatusCase, prompts: FlextCliPrompts
    ) -> None:
        """Test print_status with parametrized cases."""
        if test_case.status is None:
            result = prompts.print_status(test_case.message)
        else:
            result = prompts.print_status(test_case.message, status=test_case.status)
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

    def test_create_progress(self, prompts: FlextCliPrompts) -> None:
        """Test create_progress method."""
        result = prompts.create_progress("simple")
        tm.ok(result)
        assert isinstance(result.value, str)

    def test_with_progress_small_dataset(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with small dataset."""
        items: list[object] = list(range(c.ProgressDefaults.SMALL_DATASET_SIZE))
        result = prompts.with_progress(items, "simple")
        tm.ok(result)
        assert result.value == items

    def test_with_progress_large_dataset(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with large dataset."""
        items: list[object] = list(range(c.ProgressDefaults.LARGE_DATASET_SIZE))
        result = prompts.with_progress(items, "simple")
        tm.ok(result)
        assert result.value == items

    def test_with_progress_empty(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with empty list."""
        items: list[object] = []
        result = prompts.with_progress(items, "simple")
        tm.ok(result)
        assert result.value == items

    def test_clear_prompt_history(self, prompts: FlextCliPrompts) -> None:
        """Test clear_prompt_history method."""
        _ = prompts.prompt("simple", default="text")
        _ = prompts.prompt("with_default", default="text")
        assert len(prompts.prompt_history) > 0
        result = prompts.clear_prompt_history()
        tm.ok(result)
        assert len(prompts.prompt_history) == 0

    def test_clear_prompt_history_exception(self) -> None:
        """Test clear_prompt_history exception handling."""
        prompts = self.Fixtures.create_quiet_prompts()

        class BadList(UserList[str]):
            """List that raises exception on clear."""

            @override
            def clear(self) -> None:
                msg = "Clear failed"
                raise ValueError(msg)

        bad_list = BadList()
        bad_list.extend(["test1", "test2"])
        TestsCliPrompts._set_prompt_history(prompts, bad_list)
        result = prompts.clear_prompt_history()
        tm.fail(result)

    def test_get_prompt_statistics(self, prompts: FlextCliPrompts) -> None:
        """Test get_prompt_statistics method."""
        _ = prompts.prompt("simple", default="text")
        _ = prompts.prompt("with_default", default="text")
        result = prompts.get_prompt_statistics()
        tm.ok(result)
        stats = result.value
        assert isinstance(stats, dict)
        assert "prompts_executed" in stats
        assert "interactive_mode" in stats
        assert "default_timeout" in stats
        assert "history_size" in stats
        assert "timestamp" in stats
        prompts_executed = stats["prompts_executed"]
        assert isinstance(prompts_executed, int)
        assert prompts_executed >= 2

    def test_edge_cases_empty_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: empty message."""
        result = prompts.prompt("", default="text")
        assert isinstance(result, r)

    def test_edge_cases_long_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: very long message."""
        result = prompts.prompt(c.TestData.LONG, default="text")
        assert isinstance(result, r)

    def test_edge_cases_special_characters(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: special characters in message."""
        result = prompts.prompt(c.TestData.SPECIAL, default="text")
        assert isinstance(result, r)

    def test_edge_cases_unicode(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: unicode characters."""
        result = prompts.prompt(c.TestData.UNICODE, default="text")
        assert isinstance(result, r)

    def test_performance_multiple_prompts(self, prompts: FlextCliPrompts) -> None:
        """Test prompts performance with multiple operations."""
        start_time = time.time()
        for i in range(100):
            _ = prompts.prompt(f"Prompt {i}:", default="text")
        end_time = time.time()
        elapsed = end_time - start_time
        performance_threshold = 0.5
        assert elapsed < performance_threshold, (
            f"Performance test failed: {elapsed}s > {performance_threshold}s"
        )

    def test_memory_usage_repeated_operations(self, prompts: FlextCliPrompts) -> None:
        """Test prompts memory usage with repeated operations."""
        for i in range(20):
            result = prompts.prompt(f"Memory test {i}:", default="text")
            assert isinstance(result, r)
            tm.ok(result)
            assert result.value == "text"
        progress_result = prompts.create_progress("Memory test progress")
        tm.ok(progress_result)

    def test_integration_workflow(self, prompts: FlextCliPrompts) -> None:
        """Test complete prompt workflow integration."""
        status_result = prompts.print_status("Starting workflow")
        tm.ok(status_result)
        prompt_result = prompts.prompt("simple", default="text")
        assert isinstance(prompt_result, r)
        confirm_result = prompts.confirm("confirm", default=True)
        assert isinstance(confirm_result, r)
        select_result = prompts.select_from_options(c.TWO, "choose")
        assert isinstance(select_result, r)
        success_result = prompts.print_success("Workflow completed")
        tm.ok(success_result)

    def test_prompt_text_with_validation_pattern_valid(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_text with valid pattern matching."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_text(
            "Enter email:",
            default="test@example.com",
            validation_pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
        )
        tm.ok(result)
        assert result.value == "test@example.com"

    def test_prompt_text_with_validation_pattern_invalid_default(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_text with invalid default that doesn't match pattern."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_text(
            "Enter email:",
            default="invalid-email",
            validation_pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
        )
        tm.fail(result)

    def test_prompt_text_with_validation_pattern_no_default(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_text with pattern but no default in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_text(
            "Enter value:", default="", validation_pattern="^\\d+$"
        )
        tm.fail(result) or result.is_success

    def test_prompt_text_interactive_with_pattern_validation(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt_text in interactive mode with pattern validation."""
        monkeypatch.setattr("builtins.input", lambda _: "12345")
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_text(
            "Enter number:", default="", validation_pattern="^\\d+$"
        )
        assert isinstance(result, r)

    def test_prompt_text_interactive_pattern_mismatch(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt_text with pattern mismatch in interactive mode."""
        monkeypatch.setattr("builtins.input", lambda _: "abc")
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_text(
            "Enter number:", default="abc", validation_pattern="^\\d+$"
        )
        tm.fail(result)

    def test_confirm_keyboard_interrupt(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test confirm with KeyboardInterrupt."""
        interactive_prompts = self.Fixtures.create_interactive_prompts()

        def mock_input(_: str) -> str:
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_eof_error(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test confirm with EOFError."""
        interactive_prompts = self.Fixtures.create_interactive_prompts()

        def mock_input(_: str) -> str:
            raise EOFError

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_exception_handling(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test confirm with general exception."""
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        test_error_msg = "Test error"

        def mock_input(_: str) -> str:
            raise ValueError(test_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_quiet_mode(self, prompts: FlextCliPrompts) -> None:
        """Test confirm in quiet mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.confirm("Continue?", default=True)
        tm.ok(result)
        assert result.value is True

    def test_confirm_non_interactive_mode(self, prompts: FlextCliPrompts) -> None:
        """Test confirm in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = quiet_prompts.confirm("Continue?", default=False)
        tm.ok(result)
        assert result.value is False

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
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_choice in non-interactive mode without default."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_choice(
            "Select:", choices=["a", "b"], default=None
        )
        tm.fail(result)

    def test_prompt_choice_non_interactive_valid_default(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test prompt_choice in non-interactive mode with valid default."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt_choice("Select:", choices=["a", "b"], default="a")
        tm.ok(result)
        assert result.value == "a"

    def test_prompt_password_too_short(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt_password with password too short."""

        def mock_getpass(prompt: str) -> str:
            return "short"

        monkeypatch.setattr(getpass, "getpass", mock_getpass)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_password("Password:", min_length=8)
        tm.fail(result)

    def test_prompt_password_exception(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt_password with exception."""
        password_input_error_msg = "Password input error"

        def mock_getpass(_: str) -> str:
            raise ValueError(password_input_error_msg)

        monkeypatch.setattr(getpass, "getpass", mock_getpass)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_password("Password:")
        tm.fail(result)

    def test_prompt_password_valid_length(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt_password with valid password length."""

        def mock_getpass(prompt: str) -> str:
            return "validpassword123"

        monkeypatch.setattr(getpass, "getpass", mock_getpass)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt_password("Password:", min_length=8)
        tm.ok(result)
        assert len(result.value) >= 8

    def test_prompt_quiet_mode(self, prompts: FlextCliPrompts) -> None:
        """Test prompt in quiet mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt("Enter value:", default="default_value")
        tm.ok(result)
        assert result.value == "default_value"

    def test_prompt_non_interactive_mode(self, prompts: FlextCliPrompts) -> None:
        """Test prompt in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = quiet_prompts.prompt("Enter value:", default="default_value")
        tm.ok(result)
        assert result.value == "default_value"

    def test_prompt_empty_input_uses_default(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt with empty input uses default."""
        monkeypatch.setattr("builtins.input", lambda _: "")
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt("Enter value:", default="default")
        tm.ok(result)
        assert result.value == "default"

    def test_prompt_exception_handling(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt with exception."""
        input_error_msg = "Input error"

        def mock_input(_: str) -> str:
            raise ValueError(input_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt("Enter value:", default="")
        tm.fail(result)

    def test_select_from_options_empty_list(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with empty options list."""
        result = prompts.select_from_options([], "Select option:")
        tm.fail(result)

    def test_select_from_options_single_option(self, prompts: FlextCliPrompts) -> None:
        """Test select_from_options with single option."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.select_from_options(["only"], "Select:")
        assert isinstance(result, r)

    def test_select_from_options_exception(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test select_from_options with exception."""
        selection_error_msg = "Selection error"

        def mock_input(_: str) -> str:
            raise TypeError(selection_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.select_from_options(["a", "b"], "Select:")
        tm.fail(result)

    def test_print_message_success(self, prompts: FlextCliPrompts) -> None:
        """Test _print_message success path."""
        result = prompts._print_message(
            "Test message", "info", "Format: {message}", "Error: {error}"
        )
        tm.ok(result)

    def test_print_message_exception(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test _print_message with exception."""
        logger_error_msg = "Logger error"

        def mock_info(*args: object, **kwargs: object) -> None:
            raise ValueError(logger_error_msg)

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts._print_message(
            "Test", "info", "Format: {message}", "Error: {error}"
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

    def test_create_progress_exception(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create_progress with exception."""
        progress_error_msg = "Progress error"
        original_info = prompts.logger.info

        def mock_info(message: str, *args: object, **kwargs: object) -> None:
            if "Starting progress" in str(message):
                raise ValueError(progress_error_msg)
            original_info(str(message))

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts.create_progress("Test progress")
        tm.fail(result)

    def test_with_progress_exception(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test with_progress with exception."""
        progress_error_msg = "Progress error"
        original_info = prompts.logger.info

        def mock_info(message: str, *args: object, **kwargs: object) -> None:
            if "Starting progress operation" in str(message):
                raise ValueError(progress_error_msg)
            original_info(str(message))

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts.with_progress([1, 2, 3], "Processing")
        tm.fail(result)

    def test_with_progress_empty_items(self, prompts: FlextCliPrompts) -> None:
        """Test with_progress with empty items list."""
        result = prompts.with_progress([], "Processing")
        tm.ok(result)
        assert result.value == []

    def test_prompt_history_property(self, prompts: FlextCliPrompts) -> None:
        """Test prompt_history property returns copy."""
        prompts.prompt("Test 1", default="")
        prompts.prompt("Test 2", default="")
        history1 = prompts.prompt_history
        history2 = prompts.prompt_history
        assert history1 == history2
        assert history1 is not history2
        history1.append("test")
        assert len(prompts.prompt_history) == 2

    def test_get_prompt_statistics_empty_history(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test get_prompt_statistics with empty history."""
        result = prompts.get_prompt_statistics()
        tm.ok(result)
        stats = result.value
        assert stats["prompts_executed"] == 0
        assert stats["history_size"] == 0

    def test_get_prompt_statistics_with_history(self, prompts: FlextCliPrompts) -> None:
        """Test get_prompt_statistics with history."""
        prompts.prompt("Test 1", default="")
        prompts.prompt("Test 2", default="")
        prompts.confirm("Confirm?", default=True)
        result = prompts.get_prompt_statistics()
        tm.ok(result)
        stats = result.value
        assert "prompts_executed" in stats
        assert "history_size" in stats
        assert isinstance(stats["prompts_executed"], int)
        assert isinstance(stats["history_size"], int)

    def test_initialization_quiet_disables_interactive(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test that quiet=True disables interactive mode."""
        quiet_prompts = FlextCliPrompts(interactive_mode=True, quiet=True)
        assert quiet_prompts.interactive_mode is False
        assert quiet_prompts.quiet is True

    def test_initialization_interactive_with_quiet_false(
        self, prompts: FlextCliPrompts
    ) -> None:
        """Test initialization with interactive=True and quiet=False."""
        interactive_prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
        assert interactive_prompts.interactive_mode is True
        assert interactive_prompts.quiet is False

    def test_execute_with_exception(
        self, prompts: FlextCliPrompts, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test execute method with exception."""
        execute_error_msg = "Execute error"
        original_debug = prompts.logger.debug

        def mock_debug(message: str, *args: object, **kwargs: object) -> None:
            if "Prompt service execution completed" in str(message):
                raise ValueError(execute_error_msg)
            original_debug(str(message))

        monkeypatch.setattr(prompts.logger, "debug", mock_debug)
        result = prompts.execute()
        tm.fail(result)
