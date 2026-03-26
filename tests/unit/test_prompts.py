"""FLEXT CLI Prompts Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliPrompts covering all real functionality with flext_tests
integration, comprehensive prompt operations, and targeting 100% coverage.

Modules tested: FlextCliPrompts (prompts service)
Scope: All prompt methods, initialization, edge cases

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
from tests import (
    c,
    m,
    t,
)

T = TypeVar("T")


class TestsCliPrompts:
    """Comprehensive tests for FlextCliPrompts functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

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

    @pytest.fixture
    def prompts(self) -> FlextCliPrompts:
        """Create FlextCliPrompts instance for testing in non-interactive mode."""
        return self.Fixtures.create_quiet_prompts()

    @pytest.fixture
    def interactive_prompts(self) -> FlextCliPrompts:
        """Create FlextCliPrompts instance for interactive testing."""
        return self.Fixtures.create_interactive_prompts()

    def test_execute_success(self, prompts: FlextCliPrompts) -> None:
        """Test execute method returns success."""
        result = prompts.execute()
        tm.ok(result)
        tm.that(result.value, is_=dict)

    def test_prompt_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method with default value."""
        result = prompts.prompt("simple", default="text")
        tm.that(result, is_=r)

    def test_prompt_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test prompt method without default."""
        result = prompts.prompt("simple")
        tm.that(result, is_=r)

    def test_confirm_with_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method with default."""
        result = prompts.confirm("confirm", default=True)
        tm.that(result, is_=r)

    def test_confirm_no_default(self, prompts: FlextCliPrompts) -> None:
        """Test confirm method without default."""
        result = prompts.confirm("confirm")
        tm.that(result, is_=r)

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
        tm.that(result.value, eq="a")

    def test_prompt_choice_no_default_required(self) -> None:
        """Test prompt_choice without default triggers INTERACTIVE_MODE_DISABLED_CHOICE error."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_choice("choose", c.Cli.Test.TWO)
        tm.fail(result, has="Interactive mode disabled")

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
        tm.that({"simple", "complex", "advanced"}, has=result.value)

    def test_prompt_choice_exception_handling(self) -> None:
        """Test prompt_choice exception handler."""
        prompts = self.Fixtures.create_interactive_prompts()

        result = prompts.prompt_choice("choose", c.Cli.Test.TWO, default="choice")
        tm.fail(result)

    def test_prompt_password_non_interactive_failure(self) -> None:
        """Test prompt_password in non-interactive mode fails."""
        prompts = self.Fixtures.create_quiet_prompts()
        result = prompts.prompt_password(c.Cli.Test.TestData.PASSWORD)
        tm.fail(result, has="Interactive mode disabled")

    def test_prompt_password_min_length(self) -> None:
        """Test prompt_password with min_length validation."""
        prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = prompts.prompt_password(
            c.Cli.Test.TestData.PASSWORD,
            min_length=c.Cli.Test.PasswordDefaults.MIN_LENGTH_STRICT,
        )
        tm.that(result, is_=r)

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
            raise ValueError(test_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        result = interactive_prompts.confirm("Continue?", default=False)
        tm.fail(result)

    def test_confirm_quiet_mode(self, prompts: FlextCliPrompts) -> None:
        """Test confirm in quiet mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.confirm("Continue?", default=True)
        tm.ok(result)
        tm.that(result.value is True, eq=True)

    def test_confirm_non_interactive_mode(self, prompts: FlextCliPrompts) -> None:
        """Test confirm in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = quiet_prompts.confirm("Continue?", default=False)
        tm.ok(result)
        tm.that(result.value is False, eq=True)

    def test_prompt_password_too_short(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt_password with password too short."""

        def mock_getpass(prompt: str) -> str:
            return "short"

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
            raise ValueError(password_input_error_msg)

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
        tm.that(len(result.value), gte=8)

    def test_prompt_quiet_mode(self, prompts: FlextCliPrompts) -> None:
        """Test prompt in quiet mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts()
        result = quiet_prompts.prompt("Enter value:", default="default_value")
        tm.ok(result)
        tm.that(result.value, eq="default_value")

    def test_prompt_non_interactive_mode(self, prompts: FlextCliPrompts) -> None:
        """Test prompt in non-interactive mode."""
        quiet_prompts = self.Fixtures.create_quiet_prompts(interactive_mode=False)
        result = quiet_prompts.prompt("Enter value:", default="default_value")
        tm.ok(result)
        tm.that(result.value, eq="default_value")

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
        tm.that(result.value, eq="default")

    def test_prompt_exception_handling(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test prompt with exception."""
        input_error_msg = "Input error"

        def mock_input(_: str) -> str:
            raise ValueError(input_error_msg)

        monkeypatch.setattr("builtins.input", mock_input)
        interactive_prompts = self.Fixtures.create_interactive_prompts()
        result = interactive_prompts.prompt("Enter value:", default="")
        tm.fail(result)

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
        logger_error_msg = "Logger error"

        def mock_info(*args: t.Scalar, **kwargs: t.Scalar) -> None:
            raise ValueError(logger_error_msg)

        monkeypatch.setattr(prompts.logger, "info", mock_info)
        result = prompts._print_message(
            "Test",
            "info",
            "Format: {message}",
            "Error: {error}",
        )
        tm.fail(result)

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

    def test_edge_cases_empty_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: empty message."""
        result = prompts.prompt("", default="text")
        tm.that(result, is_=r)

    def test_edge_cases_long_message(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: very long message."""
        result = prompts.prompt(c.Cli.Test.TestData.LONG, default="text")
        tm.that(result, is_=r)

    def test_edge_cases_special_characters(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: special characters in message."""
        result = prompts.prompt(c.Cli.Test.TestData.SPECIAL, default="text")
        tm.that(result, is_=r)

    def test_edge_cases_unicode(self, prompts: FlextCliPrompts) -> None:
        """Test edge case: unicode characters."""
        result = prompts.prompt(c.Cli.Test.TestData.UNICODE, default="text")
        tm.that(result, is_=r)

    def test_performance_multiple_prompts(self, prompts: FlextCliPrompts) -> None:
        """Test prompts performance with multiple operations."""
        start_time = time.time()
        for i in range(100):
            _ = prompts.prompt(f"Prompt {i}:", default="text")
        end_time = time.time()
        elapsed = end_time - start_time
        performance_threshold = 0.5
        tm.that(elapsed, lt=performance_threshold)

    def test_memory_usage_repeated_operations(self, prompts: FlextCliPrompts) -> None:
        """Test prompts memory usage with repeated operations."""
        for i in range(20):
            result = prompts.prompt(f"Memory test {i}:", default="text")
            tm.that(result, is_=r)
            tm.ok(result)
            tm.that(result.value, eq="text")

    def test_execute_with_exception(
        self,
        prompts: FlextCliPrompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test execute method with exception."""
        execute_error_msg = "Execute error"
        original_debug = prompts.logger.debug

        def mock_debug(message: str, *args: t.Scalar, **kwargs: t.Scalar) -> None:
            if "Prompt service execution completed" in str(message):
                raise ValueError(execute_error_msg)
            original_debug(str(message))

        monkeypatch.setattr(prompts.logger, "debug", mock_debug)
        result = prompts.execute()
        tm.fail(result)
