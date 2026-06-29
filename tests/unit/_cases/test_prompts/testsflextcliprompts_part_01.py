"""Behavioral tests for the prompts service."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from flext_tests import tm
from tests.constants import c
from tests.protocols import p


class TestsFlextCliPrompts:
    """Implementation part for TestsFlextCliPrompts."""

    def test_execute_success(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
    ) -> None:
        prompts = make_prompts(interactive_mode=False)
        result = prompts.execute()
        tm.ok(result)
        tm.that(result.value[c.Cli.DICT_KEY_STATUS], eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(result.value[c.Cli.DICT_KEY_SERVICE], eq=c.Cli.FLEXT_CLI)

    def test_execute_uses_public_cmd_status_even_when_prompt_logger_would_fail(
        self,
        make_failing_prompts: Callable[..., p.Tests.FailingLogPrompts],
    ) -> None:
        prompts = make_failing_prompts(interactive_mode=False)
        prompts.fail_on_log(level=c.LogLevel.DEBUG, message="Execute error")
        result = prompts.execute()
        tm.ok(result)
        tm.that(result.value[c.Cli.DICT_KEY_STATUS], eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(result.value[c.Cli.DICT_KEY_SERVICE], eq=c.Cli.FLEXT_CLI)

    def test_prompt_returns_default_in_quiet_and_non_interactive_modes(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
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
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
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
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
    ) -> None:
        prompts = make_prompts().use_input_error(ValueError("Input error"))
        result = prompts.prompt("Enter value")
        tm.fail(result, has="Input error")

    def test_confirm_returns_defaults_when_not_interactive(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
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
        make_capture_prompts: Callable[..., p.Tests.CaptureLogPrompts],
    ) -> None:
        prompts = make_capture_prompts()
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
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
        error: Exception,
        expected: str,
    ) -> None:
        prompts = make_prompts().use_input_error(error)
        result = prompts.confirm("Continue?", default=False)
        tm.fail(result, has=expected)


__all__: list[str] = ["TestsFlextCliPrompts"]
