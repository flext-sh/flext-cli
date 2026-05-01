"""Focused coverage checks for prompt-side logging behavior."""

from __future__ import annotations

from typing import Self

from flext_tests import tm

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

    def test_prompt_choice_fails_with_empty_choices(self) -> None:
        """Test that prompt_choice handles empty choices (real API failure)."""
        prompts = _CaptureLogPrompts().configure_state(interactive=True)
        result = prompts.prompt_choice(
            "Choose one",
            choices=(),
            default=None,
        )
        tm.fail(result)

    def test_prompt_choice_fails_with_default_not_in_choices(self) -> None:
        """Test that prompt_choice handles invalid default (real API failure)."""
        prompts = _CaptureLogPrompts().configure_state(interactive=True)
        result = prompts.prompt_choice(
            "Choose one",
            choices=("a", "b"),
            default="z",
        )
        tm.fail(result)
