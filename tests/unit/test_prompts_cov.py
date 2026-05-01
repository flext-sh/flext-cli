"""Focused coverage checks for prompt-side logging behavior."""

from __future__ import annotations

from typing import Self

import pytest
from flext_tests import tm

import flext_cli.services.prompts as prompts_service_module
from tests.helpers._impl import TestsFlextCliCaptureLogPrompts


class _CaptureLogPrompts(TestsFlextCliCaptureLogPrompts):
    """Prompt service that records log calls and supports test-env override."""

    _test_env_override: bool | None = True

    def force_non_test_env(self) -> Self:
        self._test_env_override = False
        return self


class TestsFlextCliPromptsCov:
    """Behavior contract for prompt logging coverage."""

    def test_prompt_logs_input_when_not_in_test_env(self) -> None:
        prompts = (
            _CaptureLogPrompts()
            .configure_state(interactive=True)
            .use_input_values(["typed"])
            .force_non_test_env()
        )
        result = prompts.prompt("message", default="default")
        tm.ok(result)
        tm.that(result.value, eq="typed")
        messages: list[str] = [message for _, message in prompts.records]
        tm.that(messages, has=["User input for 'message': typed"])

    def test_confirm_records_warning_before_retrying(self) -> None:
        prompts = (
            _CaptureLogPrompts()
            .configure_state(interactive=True)
            .use_input_values(["maybe", "y"])
        )
        result = prompts.confirm("m", default=False)
        tm.ok(result)
        tm.that(result.value, eq=True)
        messages: list[str] = [message for _, message in prompts.records]
        tm.that(
            messages,
            has=["Invalid confirmation input - please enter yes or no"],
        )

    def test_prompt_choice_handles_internal_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        prompts = _CaptureLogPrompts().configure_state(interactive=True)
        monkeypatch.setattr(
            prompts_service_module.u.Cli,
            "prompts_choice_result",
            lambda **_kwargs: (_ for _ in ()).throw(ValueError("choice boom")),
        )
        result = prompts.prompt_choice("Choose one", choices=("a", "b"), default="a")
        tm.fail(result, has="choice boom")
        messages: list[str] = [message for _, message in prompts.records]
        tm.that(
            messages,
            has=["FATAL ERROR during prompt_choice - operation aborted"],
        )
