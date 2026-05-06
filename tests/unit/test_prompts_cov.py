"""Focused coverage checks for prompt-side logging behavior."""

from __future__ import annotations

from collections.abc import Callable

from flext_tests import tm

from tests import p


class TestsFlextCliPromptsCov:
    """Behavior contract for prompt logging coverage."""

    def test_prompt_logs_input_when_not_in_test_env(
        self,
        make_capture_prompts: Callable[..., p.Tests.CaptureLogPrompts],
    ) -> None:
        prompts = (
            make_capture_prompts(interactive_mode=True)
            .use_input_values(["typed"])
            .override_test_env(enabled=False)
        )
        result = prompts.prompt("message", default="default")
        tm.ok(result)
        tm.that(result.value, eq="typed")
        messages: list[str] = [message for _, message in prompts.records]
        tm.that(messages, has=["User input for 'message': typed"])

    def test_confirm_records_warning_before_retrying(
        self,
        make_capture_prompts: Callable[..., p.Tests.CaptureLogPrompts],
    ) -> None:
        prompts = (
            make_capture_prompts(interactive_mode=True)
            .use_input_values(["maybe", "y"])
            .override_test_env()
        )
        result = prompts.confirm("m", default=False)
        tm.ok(result)
        tm.that(result.value, eq=True)
        messages: list[str] = [message for _, message in prompts.records]
        tm.that(
            messages,
            has=["Invalid confirmation input - please enter yes or no"],
        )

    def test_prompt_choice_fails_with_empty_choices(
        self,
        make_capture_prompts: Callable[..., p.Tests.CaptureLogPrompts],
    ) -> None:
        """Test that prompt_choice handles empty choices (real API failure)."""
        prompts = make_capture_prompts(interactive_mode=True).override_test_env()
        result = prompts.prompt_choice(
            "Choose one",
            choices=(),
            default=None,
        )
        tm.fail(result)

    def test_prompt_choice_fails_with_default_not_in_choices(
        self,
        make_capture_prompts: Callable[..., p.Tests.CaptureLogPrompts],
    ) -> None:
        """Test that prompt_choice handles invalid default (real API failure)."""
        prompts = make_capture_prompts(interactive_mode=True).override_test_env()
        result = prompts.prompt_choice(
            "Choose one",
            choices=("a", "b"),
            default="z",
        )
        tm.fail(result)
