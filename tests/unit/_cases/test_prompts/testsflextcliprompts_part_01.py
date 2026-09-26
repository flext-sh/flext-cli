"""Behavioral tests for the prompts service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests import c

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests import p


class TestsFlextCliPrompts:
    """Implementation part for TestsFlextCliPrompts."""

    def test_execute_success(self, make_prompts: Callable[..., p.Tests.Prompts]) -> None:
        """Verify that execute success."""
        prompts = make_prompts(interactive_mode=False)
        result = prompts.execute()
        tm.ok(result)
        tm.that(result.value.status, eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(result.value.service, eq=c.Cli.FLEXT_CLI)

    def test_prompt_returns_default_in_quiet_and_non_interactive_modes(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that prompt returns default in quiet and non interactive modes."""
        quiet_prompts = make_prompts(quiet=True)
        tm.that(
            quiet_prompts.prompt("Enter value", default="default").value, eq="default"
        )
        non_interactive_prompts = make_prompts(interactive_mode=False)
        tm.that(
            non_interactive_prompts.prompt("Enter value", default="fallback").value,
            eq="fallback",
        )

    def test_prompt_reads_input_and_uses_default_for_empty_text(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that prompt reads input and uses default for empty text."""
        prompts = make_prompts(inputs=[" typed ", ""])
        typed_result = prompts.prompt("Enter value")
        tm.ok(typed_result)
        tm.that(typed_result.value, eq="typed")
        default_result = prompts.prompt("Enter value", default="default")
        tm.ok(default_result)
        tm.that(default_result.value, eq="default")

    def test_prompt_handles_input_failure(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that prompt handles input failure."""
        prompts = make_prompts(error=ValueError("Input error"))
        result = prompts.prompt("Enter value")
        tm.fail(result, has="Input error")

    def test_confirm_returns_defaults_when_not_interactive(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that confirm returns defaults when not interactive."""
        quiet_prompts = make_prompts(quiet=True)
        tm.that(quiet_prompts.confirm("Continue?", default=True).value, eq=True)
        non_interactive_prompts = make_prompts(interactive_mode=False)
        tm.that(
            non_interactive_prompts.confirm("Continue?", default=False).value, eq=False
        )

    def test_confirm_accepts_yes_no_default_and_invalid_retry(
        self, make_prompts: Callable[..., p.Tests.Prompts]
    ) -> None:
        """Verify that confirm accepts yes no default and invalid retry."""
        prompts = make_prompts(inputs=["", "y", "n", "maybe", "yes"])
        tm.that(prompts.confirm("Continue?", default=True).value, eq=True)
        tm.that(prompts.confirm("Continue?", default=False).value, eq=True)
        tm.that(prompts.confirm("Continue?", default=True).value, eq=False)
        retry_result = prompts.confirm("Continue?", default=False)
        tm.ok(retry_result)
        tm.that(retry_result.value, eq=True)

    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (KeyboardInterrupt(), c.Cli.ERR_USER_CANCELLED_CONFIRMATION),
            (EOFError(), c.Cli.ERR_INPUT_STREAM_ENDED),
            (ValueError("Test error"), "Test error"),
        ],
    )
    def test_confirm_handles_failures(
        self,
        make_prompts: Callable[..., p.Tests.Prompts],
        error: Exception,
        expected: str,
    ) -> None:
        """Verify that confirm handles failures."""
        prompts = make_prompts(error=error)
        result = prompts.confirm("Continue?", default=False)
        tm.fail(result, has=expected)

    def test_prompt_password_paths(
        self,
        make_prompts: Callable[..., p.Tests.Prompts],
        scripted_password_pair: Callable[[], tuple[str, str]],
    ) -> None:
        """Verify that prompt password paths."""
        short_secret, valid_secret = scripted_password_pair()
        tm.fail(
            make_prompts(interactive_mode=False).prompt_password("Password:"),
            has=c.Cli.ERR_INTERACTIVE_PASSWORD_DISABLED,
        )
        short_prompts = make_prompts(password=short_secret)
        short_result = short_prompts.prompt_password("Password:", min_length=8)
        tm.fail(short_result)
        valid_prompts = make_prompts(password=valid_secret)
        valid_result = valid_prompts.prompt_password("Password:", min_length=8)
        tm.ok(valid_result)
        tm.that(valid_result.value, eq=valid_secret)
        failing_prompts = make_prompts(error=ValueError("Password input error"))
        tm.fail(
            failing_prompts.prompt_password("Password:"), has="Password input error"
        )


__all__: list[str] = ["TestsFlextCliPrompts"]
