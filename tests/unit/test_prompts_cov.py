"""Behavioral contract tests for the prompts service public API.

Every assertion targets observable public behavior: the ``r[T]`` outcome of
``prompt`` / ``confirm`` / ``prompt_choice`` / ``prompt_password`` (success value
or failure error), never internal logging side-effects or private state. Input
readers are injected at the genuine stdin boundary via the scripted test double.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_tests import tm
from tests import c

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests import p


class TestsFlextCliPromptsCov:
    """Behavior contract for the prompt service public surface."""

    def test_prompt_returns_typed_input_regardless_of_test_env(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt returns typed input regardless of test env."""
        prompts = (
            make_prompts(interactive_mode=True)
            .use_input_values(["typed"])
            .override_test_env(enabled=False)
        )
        result = prompts.prompt("message", default="default")
        tm.ok(result)
        tm.that(result.value, eq="typed")

    @pytest.mark.parametrize(
        ("raw_input", "default", "expected"),
        [
            ("typed", "fallback", "typed"),
            ("  spaced  ", "fallback", "spaced"),
            ("", "fallback", "fallback"),
            ("   ", "fallback", "fallback"),
        ],
    )
    def test_prompt_normalizes_input_and_falls_back_to_default(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
        raw_input: str,
        default: str,
        expected: str,
    ) -> None:
        """Verify that prompt normalizes input and falls back to default."""
        prompts = make_prompts(interactive_mode=True).use_input_values([raw_input])
        result = prompts.prompt("message", default=default)
        tm.ok(result)
        tm.that(result.value, eq=expected)

    @pytest.mark.parametrize("quiet", [True, False])
    def test_prompt_returns_default_when_non_interactive(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts], *, quiet: bool
    ) -> None:
        """Verify that prompt returns default when non interactive."""
        prompts = make_prompts(interactive_mode=False, quiet=quiet)
        result = prompts.prompt("message", default="fallback")
        tm.ok(result)
        tm.that(result.value, eq="fallback")

    def test_prompt_fails_when_input_reader_raises(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt fails when input reader raises."""
        prompts = make_prompts(interactive_mode=True).use_input_error(
            ValueError("boom")
        )
        result = prompts.prompt("message", default="default")
        tm.fail(result, has="boom")

    @pytest.mark.parametrize(
        ("answer", "default", "expected"),
        [
            ("y", False, True),
            ("yes", False, True),
            ("n", True, False),
            ("no", True, False),
            ("", True, True),
            ("", False, False),
        ],
    )
    def test_confirm_parses_yes_no_and_default(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
        answer: str,
        *,
        expected: bool,
        default: bool,
    ) -> None:
        """Verify that confirm parses yes no and default."""
        prompts = make_prompts(interactive_mode=True).use_input_values([answer])
        result = prompts.confirm("message", default=default)
        tm.ok(result)
        tm.that(result.value, eq=expected)

    def test_confirm_retries_past_invalid_input_until_valid(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that confirm retries past invalid input until valid."""
        prompts = make_prompts(interactive_mode=True).use_input_values([
            "maybe",
            "huh",
            "y",
        ])
        result = prompts.confirm("message", default=False)
        tm.ok(result)
        tm.that(result.value, eq=True)

    @pytest.mark.parametrize("default", [True, False])
    def test_confirm_returns_default_when_non_interactive(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts], *, default: bool
    ) -> None:
        """Verify that confirm returns default when non interactive."""
        prompts = make_prompts(interactive_mode=False)
        result = prompts.confirm("message", default=default)
        tm.ok(result)
        tm.that(result.value, eq=default)

    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (KeyboardInterrupt(), c.Cli.ERR_USER_CANCELLED_CONFIRMATION),
            (EOFError(), c.Cli.ERR_INPUT_STREAM_ENDED),
            (ValueError("bad"), "bad"),
        ],
    )
    def test_confirm_fails_on_input_errors(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
        error: Exception,
        expected: str,
    ) -> None:
        """Verify that confirm fails on input errors."""
        prompts = make_prompts(interactive_mode=True).use_input_error(error)
        result = prompts.confirm("message", default=False)
        tm.fail(result, has=expected)

    def test_prompt_choice_returns_default_when_present(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt choice returns default when present."""
        prompts = make_prompts(interactive_mode=True)
        result = prompts.prompt_choice("Choose", choices=("a", "b"), default="a")
        tm.ok(result)
        tm.that(result.value, eq="a")

    def test_prompt_choice_fails_with_empty_choices(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt choice fails with empty choices."""
        prompts = make_prompts(interactive_mode=True)
        result = prompts.prompt_choice("Choose", choices=(), default=None)
        tm.fail(result, has=c.Cli.ERR_NO_CHOICES)

    def test_prompt_choice_fails_when_default_not_in_choices(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt choice fails when default not in choices."""
        prompts = make_prompts(interactive_mode=True)
        result = prompts.prompt_choice("Choose", choices=("a", "b"), default="z")
        tm.fail(result, has="z")

    def test_prompt_choice_fails_when_default_required(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt choice fails when default required."""
        prompts = make_prompts(interactive_mode=True)
        result = prompts.prompt_choice("Choose", choices=("a", "b"), default=None)
        tm.fail(result)

    def test_prompt_password_returns_value_meeting_min_length(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt password returns value meeting min length."""
        prompts = make_prompts(interactive_mode=True).use_password("s3cret")
        result = prompts.prompt_password("Password:", min_length=4)
        tm.ok(result)
        tm.that(result.value, eq="s3cret")

    def test_prompt_password_fails_when_too_short(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt password fails when too short."""
        prompts = make_prompts(interactive_mode=True).use_password("ab")
        result = prompts.prompt_password("Password:", min_length=5)
        tm.fail(result)

    def test_prompt_password_fails_when_non_interactive(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt password fails when non interactive."""
        prompts = make_prompts(interactive_mode=False)
        result = prompts.prompt_password("Password:")
        tm.fail(result, has=c.Cli.ERR_INTERACTIVE_PASSWORD_DISABLED)

    def test_prompt_password_fails_when_reader_raises(
        self, make_prompts: Callable[..., p.Tests.ScriptedPrompts]
    ) -> None:
        """Verify that prompt password fails when reader raises."""
        prompts = make_prompts(interactive_mode=True).use_password_error(
            ValueError("no tty")
        )
        result = prompts.prompt_password("Password:")
        tm.fail(result, has="no tty")


__all__: list[str] = ["TestsFlextCliPromptsCov"]
