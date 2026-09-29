"""Behavioral tests for the prompts service."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests import c

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests import p


class TestsFlextCliPrompts:
    """Implementation part for TestsFlextCliPrompts."""

    def test_prompt_choice_paths(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that prompt choice paths."""
        quiet_prompts = make_prompts(interactive_mode=False)
        tm.fail(
            quiet_prompts.prompt_choice(choices=[], default=None),
            has=c.Cli.ERR_NO_CHOICES,
        )
        tm.fail(
            quiet_prompts.prompt_choice(choices=["a", "b"], default=None),
            has=c.Cli.ERR_INTERACTIVE_CHOICE_DISABLED,
        )
        valid_default = quiet_prompts.prompt_choice(choices=["a", "b"], default="a")
        tm.ok(valid_default)
        tm.that(valid_default.value, eq="a")
        interactive_prompts = make_prompts()
        required = interactive_prompts.prompt_choice(
            choices=["alpha", "beta"], default=None
        )
        tm.fail(required, has="alpha")
        tm.fail(required, has="beta")
        tm.fail(
            interactive_prompts.prompt_choice(choices=["a", "b"], default="c"),
            has=c.Cli.ERR_INVALID_CHOICE_FMT.format(choice="c"),
        )
        selected = interactive_prompts.prompt_choice(
            choices=["simple", "complex", "advanced"], default="simple"
        )
        tm.ok(selected)
        tm.that(selected.value, eq="simple")

    def test_print_helpers_paths(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that print helpers paths."""
        prompts = make_prompts()
        tm.ok(prompts.print_success("simple"))
        tm.ok(prompts.print_error("simple"))
        tm.ok(prompts.print_warning("simple"))

    @pytest.mark.parametrize("message", c.Tests.PROMPT_EDGE_MESSAGES)
    def test_prompt_accepts_edge_case_messages(
        self, make_prompts: Callable[..., p.Tests.Prompts], message: str
    ) -> None:
        """Verify that prompt accepts edge case messages."""
        prompts = make_prompts(interactive_mode=False)
        result = prompts.prompt(message, default="text")
        tm.ok(result)
        tm.that(result.value, eq="text")

    def test_repeated_prompt_operations_remain_fast(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that repeated prompt operations remain fast."""
        prompts = make_prompts(interactive_mode=False)
        started_at = time.time()
        for index in range(100):
            result = prompts.prompt(f"Prompt {index}", default="text")
            tm.ok(result)
            tm.that(result.value, eq="text")
        tm.that(time.time() - started_at, lt=0.5)


__all__: list[str] = ["TestsFlextCliPrompts"]
