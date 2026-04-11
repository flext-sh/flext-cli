"""Behavioral tests for the prompts service."""

from __future__ import annotations

import time
from typing import Self, override

import pytest
from flext_tests import tm
from pydantic import PrivateAttr

from flext_cli import FlextCliPrompts, m
from tests import c, t


class ScriptedPrompts(FlextCliPrompts):
    """Prompt service with typed scripting helpers."""

    def use_input_values(self, values: t.StrSequence) -> Self:
        values_iter = iter(values)
        self._input_reader = lambda _prompt: next(values_iter)
        return self

    def use_input_error(self, error: Exception) -> Self:
        def raise_input(_prompt: str) -> str:
            raise error

        self._input_reader = raise_input
        return self

    def use_password(self, password: str) -> Self:
        self._password_reader = lambda _prompt: password
        return self

    def use_password_error(self, error: Exception) -> Self:
        def raise_password(_prompt: str) -> str:
            raise error

        self._password_reader = raise_password
        return self

    def configure_state(self, *, interactive: bool = True, quiet: bool = False) -> Self:
        return self.configure(
            m.Cli.PromptRuntimeState(
                interactive=interactive,
                quiet=quiet,
            ),
        )


class CaptureLogPrompts(ScriptedPrompts):
    """Prompt service that captures log calls without writing to the real logger."""

    _records: list[tuple[str, str]] = PrivateAttr(default_factory=list)

    @property
    def records(self) -> list[tuple[str, str]]:
        return self._records

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **_context: t.ContainerValue,
    ) -> None:
        self._records.append((log_level, message))


class FailingLogPrompts(ScriptedPrompts):
    """Prompt service that fails on one selected log level."""

    _failure_level: str = PrivateAttr(default="")
    _failure_message: str = PrivateAttr(default="logger failure")

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.ContainerValue,
    ) -> None:
        if log_level == self._failure_level:
            raise ValueError(self._failure_message)
        super()._log(log_level, message, **context)


class TestsCliPrompts:
    """Behavior-only tests for FlextCliPrompts."""

    class Fixtures:
        """Small factories for direct prompt scripting."""

        @staticmethod
        def create(
            prompt_type: type[ScriptedPrompts] = ScriptedPrompts,
            *,
            interactive_mode: bool = True,
            quiet: bool = False,
        ) -> ScriptedPrompts:
            return prompt_type().configure_state(
                interactive=interactive_mode,
                quiet=quiet,
            )

    def test_execute_success(self) -> None:
        prompts = self.Fixtures.create(interactive_mode=False)
        result = prompts.execute()
        tm.ok(result)
        tm.that(result.value, eq={})

    def test_execute_failure_when_debug_logging_crashes(self) -> None:
        prompts = self.Fixtures.create(FailingLogPrompts, interactive_mode=False)
        assert isinstance(prompts, FailingLogPrompts)
        prompts._failure_level = c.LogLevel.DEBUG
        prompts._failure_message = "Execute error"
        result = prompts.execute()
        tm.fail(result, has="Execute error")

    def test_prompt_returns_default_in_quiet_and_non_interactive_modes(self) -> None:
        quiet_prompts = self.Fixtures.create(quiet=True)
        tm.that(
            quiet_prompts.prompt("Enter value", default="default").value, eq="default"
        )
        non_interactive_prompts = self.Fixtures.create(interactive_mode=False)
        tm.that(
            non_interactive_prompts.prompt("Enter value", default="fallback").value,
            eq="fallback",
        )

    def test_prompt_reads_input_and_uses_default_for_empty_text(self) -> None:
        prompts = self.Fixtures.create().use_input_values([" typed ", ""])
        typed_result = prompts.prompt("Enter value")
        tm.ok(typed_result)
        tm.that(typed_result.value, eq="typed")
        default_result = prompts.prompt("Enter value", default="default")
        tm.ok(default_result)
        tm.that(default_result.value, eq="default")

    def test_prompt_handles_input_failure(self) -> None:
        prompts = self.Fixtures.create().use_input_error(ValueError("Input error"))
        result = prompts.prompt("Enter value")
        tm.fail(result, has="Input error")

    def test_confirm_returns_defaults_when_not_interactive(self) -> None:
        quiet_prompts = self.Fixtures.create(quiet=True)
        tm.that(quiet_prompts.confirm("Continue?", default=True).value, eq=True)
        non_interactive_prompts = self.Fixtures.create(interactive_mode=False)
        tm.that(
            non_interactive_prompts.confirm("Continue?", default=False).value,
            eq=False,
        )

    def test_confirm_accepts_yes_no_default_and_invalid_retry(self) -> None:
        prompts = self.Fixtures.create(CaptureLogPrompts)
        assert isinstance(prompts, CaptureLogPrompts)
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
        error: Exception,
        expected: str,
    ) -> None:
        prompts = self.Fixtures.create().use_input_error(error)
        result = prompts.confirm("Continue?", default=False)
        tm.fail(result, has=expected)

    def test_prompt_choice_paths(self) -> None:
        quiet_prompts = self.Fixtures.create(interactive_mode=False)
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
        interactive_prompts = self.Fixtures.create()
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

    def test_prompt_password_paths(self) -> None:
        tm.fail(
            self.Fixtures.create(interactive_mode=False).prompt_password("Password:"),
            has="Interactive mode disabled",
        )
        short_prompts = self.Fixtures.create().use_password("short")
        tm.fail(
            short_prompts.prompt_password("Password:", min_length=8), has="too short"
        )
        valid_prompts = self.Fixtures.create().use_password("validpassword123")
        valid_result = valid_prompts.prompt_password("Password:", min_length=8)
        tm.ok(valid_result)
        tm.that(len(valid_result.value), gte=8)
        failing_prompts = self.Fixtures.create().use_password_error(
            ValueError("Password input error"),
        )
        tm.fail(
            failing_prompts.prompt_password("Password:"), has="Password input error"
        )

    def test_print_helpers_paths(self) -> None:
        prompts = self.Fixtures.create()
        tm.ok(prompts.print_success("simple"))
        tm.ok(prompts.print_error("simple"))
        tm.ok(prompts.print_warning("simple"))

    def test_print_helper_failure_when_logging_crashes(self) -> None:
        prompts = self.Fixtures.create(FailingLogPrompts)
        assert isinstance(prompts, FailingLogPrompts)
        prompts._failure_level = c.LogLevel.INFO
        prompts._failure_message = "Logger error"
        result = prompts.print_success("Test")
        tm.fail(result, has="Logger error")

    @pytest.mark.parametrize(
        "message",
        [
            "",
            c.Cli.Tests.TestData.LONG,
            c.Cli.Tests.TestData.SPECIAL,
            c.Cli.Tests.TestData.UNICODE,
        ],
    )
    def test_prompt_accepts_edge_case_messages(self, message: str) -> None:
        prompts = self.Fixtures.create(interactive_mode=False)
        result = prompts.prompt(message, default="text")
        tm.ok(result)
        tm.that(result.value, eq="text")

    def test_repeated_prompt_operations_remain_fast(self) -> None:
        prompts = self.Fixtures.create(interactive_mode=False)
        started_at = time.time()
        for index in range(100):
            result = prompts.prompt(f"Prompt {index}", default="text")
            tm.ok(result)
            tm.that(result.value, eq="text")
        tm.that(time.time() - started_at, lt=0.5)
