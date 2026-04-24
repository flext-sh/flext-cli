"""Behavioral tests for the prompts service."""

from __future__ import annotations

import time
from collections.abc import Callable

import pytest
from flext_tests import tm

from tests import c
from tests.helpers._impl import (
    FlextCliCaptureLogPrompts,
    FlextCliFailingLogPrompts,
    FlextCliScriptedPrompts,
)


class TestsFlextCliPrompts:
    """Behavior-only tests for FlextCliPrompts."""

    def test_execute_success(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts(interactive_mode=False)
        result = prompts.execute()
        tm.ok(result)
        tm.that(result.value, empty=True)

    def test_execute_failure_when_debug_logging_crashes(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts(FlextCliFailingLogPrompts, interactive_mode=False)
        assert isinstance(prompts, FlextCliFailingLogPrompts)
        prompts.fail_on_log(level=c.LogLevel.DEBUG, message="Execute error")
        result = prompts.execute()
        tm.fail(result, has="Execute error")

    def test_prompt_returns_default_in_quiet_and_non_interactive_modes(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        quiet_prompts = make_prompts(quiet=True)
        tm.that(
            quiet_prompts.prompt("Enter value", default="default").value,
            eq="default",
        )
        non_interactive_prompts = make_prompts(interactive_mode=False)
        tm.that(
            non_interactive_prompts.prompt("Enter value", default="fallback").value,
            eq="fallback",
        )

    def test_prompt_reads_input_and_uses_default_for_empty_text(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts().use_input_values([" typed ", ""])
        typed_result = prompts.prompt("Enter value")
        tm.ok(typed_result)
        tm.that(typed_result.value, eq="typed")
        default_result = prompts.prompt("Enter value", default="default")
        tm.ok(default_result)
        tm.that(default_result.value, eq="default")

    def test_prompt_handles_input_failure(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts().use_input_error(ValueError("Input error"))
        result = prompts.prompt("Enter value")
        tm.fail(result, has="Input error")

    def test_confirm_returns_defaults_when_not_interactive(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        quiet_prompts = make_prompts(quiet=True)
        tm.that(quiet_prompts.confirm("Continue?", default=True).value, eq=True)
        non_interactive_prompts = make_prompts(interactive_mode=False)
        tm.that(
            non_interactive_prompts.confirm("Continue?", default=False).value,
            eq=False,
        )

    def test_confirm_accepts_yes_no_default_and_invalid_retry(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts(FlextCliCaptureLogPrompts)
        assert isinstance(prompts, FlextCliCaptureLogPrompts)
        prompts.use_input_values(["", "y", "n", "maybe", "yes"])
        tm.that(prompts.confirm("Continue?", default=True).value, eq=True)
        tm.that(prompts.confirm("Continue?", default=False).value, eq=True)
        tm.that(prompts.confirm("Continue?", default=True).value, eq=False)
        retry_result = prompts.confirm("Continue?", default=False)
        tm.ok(retry_result)
        tm.that(retry_result.value, eq=True)
        messages: list[str] = [message for _, message in prompts.records]
        tm.that(
            messages,
            has=["Invalid confirmation input - please enter yes or no"],
        )

    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (KeyboardInterrupt(), "User cancelled confirmation"),
            (EOFError(), "Input stream ended"),
            (ValueError("Test error"), "Confirmation failed: Test error"),
        ],
    )
    def test_confirm_handles_failures(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
        error: Exception,
        expected: str,
    ) -> None:
        prompts = make_prompts().use_input_error(error)
        result = prompts.confirm("Continue?", default=False)
        tm.fail(result, has=expected)

    def test_prompt_choice_paths(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        quiet_prompts = make_prompts(interactive_mode=False)
        tm.fail(quiet_prompts.prompt_choice("Select:", choices=[], default=None))
        tm.fail(
            quiet_prompts.prompt_choice("Select:", choices=["a", "b"], default=None),
            has="Interactive mode disabled",
        )
        valid_default = quiet_prompts.prompt_choice(
            "Select:",
            choices=["a", "b"],
            default="a",
        )
        tm.ok(valid_default)
        tm.that(valid_default.value, eq="a")
        interactive_prompts = make_prompts()
        tm.fail(
            interactive_prompts.prompt_choice(
                "Select:", choices=["a", "b"], default=None
            ),
            has="Choice required",
        )
        tm.fail(
            interactive_prompts.prompt_choice(
                "Select:", choices=["a", "b"], default="c"
            ),
            has="Invalid choice",
        )
        selected = interactive_prompts.prompt_choice(
            "Select:",
            choices=["simple", "complex", "advanced"],
            default="simple",
        )
        tm.ok(selected)
        tm.that(selected.value, eq="simple")

    def test_prompt_password_paths(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        tm.fail(
            make_prompts(interactive_mode=False).prompt_password("Password:"),
            has="Interactive mode disabled",
        )
        short_prompts = make_prompts().use_password("short")
        tm.fail(
            short_prompts.prompt_password("Password:", min_length=8),
            has="too short",
        )
        valid_prompts = make_prompts().use_password("validpassword123")
        valid_result = valid_prompts.prompt_password("Password:", min_length=8)
        tm.ok(valid_result)
        tm.that(len(valid_result.value), gte=8)
        failing_prompts = make_prompts().use_password_error(
            ValueError("Password input error"),
        )
        tm.fail(
            failing_prompts.prompt_password("Password:"),
            has="Password input error",
        )

    def test_print_helpers_paths(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts()
        tm.ok(prompts.print_success("simple"))
        tm.ok(prompts.print_error("simple"))
        tm.ok(prompts.print_warning("simple"))

    def test_print_helper_failure_when_logging_crashes(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts(FlextCliFailingLogPrompts)
        assert isinstance(prompts, FlextCliFailingLogPrompts)
        prompts.fail_on_log(level=c.LogLevel.INFO, message="Logger error")
        result = prompts.print_success("Test")
        tm.fail(result, has="Logger error")

    @pytest.mark.parametrize(
        "message",
        [
            "",
            c.Cli.Tests.LONG,
            c.Cli.Tests.SPECIAL,
            c.Cli.Tests.UNICODE,
        ],
    )
    def test_prompt_accepts_edge_case_messages(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
        message: str,
    ) -> None:
        prompts = make_prompts(interactive_mode=False)
        result = prompts.prompt(message, default="text")
        tm.ok(result)
        tm.that(result.value, eq="text")

    def test_repeated_prompt_operations_remain_fast(
        self,
        make_prompts: Callable[..., FlextCliScriptedPrompts],
    ) -> None:
        prompts = make_prompts(interactive_mode=False)
        started_at = time.time()
        for index in range(100):
            result = prompts.prompt(f"Prompt {index}", default="text")
            tm.ok(result)
            tm.that(result.value, eq="text")
        tm.that(time.time() - started_at, lt=0.5)
