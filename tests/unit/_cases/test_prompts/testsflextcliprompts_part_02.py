"""Behavioral tests for the prompts service."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm
from tests.constants import c

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.protocols import p


class TestsFlextCliPrompts:
    """Implementation part for TestsFlextCliPrompts."""

    def test_prompt_choice_paths(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
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
                "Select:",
                choices=["a", "b"],
                default=None,
            ),
            has="Choice required",
        )
        tm.fail(
            interactive_prompts.prompt_choice(
                "Select:",
                choices=["a", "b"],
                default="c",
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
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
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
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
    ) -> None:
        prompts = make_prompts()
        tm.ok(prompts.print_success("simple"))
        tm.ok(prompts.print_error("simple"))
        tm.ok(prompts.print_warning("simple"))

    def test_print_helper_failure_when_logging_crashes(
        self,
        make_failing_prompts: Callable[..., p.Tests.FailingLogPrompts],
    ) -> None:
        prompts = make_failing_prompts()
        prompts.fail_on_log(level=c.LogLevel.INFO, message="Logger error")
        result = prompts.print_success("Test")
        tm.fail(result, has="Logger error")

    @pytest.mark.parametrize(
        "message",
        c.Tests.PROMPT_EDGE_MESSAGES,
    )
    def test_prompt_accepts_edge_case_messages(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
        message: str,
    ) -> None:
        prompts = make_prompts(interactive_mode=False)
        result = prompts.prompt(message, default="text")
        tm.ok(result)
        tm.that(result.value, eq="text")

    def test_repeated_prompt_operations_remain_fast(
        self,
        make_prompts: Callable[..., p.Tests.ScriptedPrompts],
    ) -> None:
        prompts = make_prompts(interactive_mode=False)
        started_at = time.time()
        for index in range(100):
            result = prompts.prompt(f"Prompt {index}", default="text")
            tm.ok(result)
            tm.that(result.value, eq="text")
        tm.that(time.time() - started_at, lt=0.5)


__all__: list[str] = ["TestsFlextCliPrompts"]
