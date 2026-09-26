"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from flext_cli import FlextCliPrompts, FlextCliSettings
from tests import c, m

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests import p, t


def _scripted_reader(
    values: t.StrSequence, error: Exception | None
) -> Callable[[str], str]:
    """Build an input port that replays ``values`` or raises ``error``."""
    values_iter = iter(values)

    def _read(_prompt: str) -> str:
        if error is not None:
            raise error
        return next(values_iter)

    return _read


@pytest.fixture
def make_prompts() -> Callable[..., p.Tests.Prompts]:
    """Provide prompt services wired to scripted input ports.

    ``inputs`` feeds the text port, ``password`` the secret port, and ``error``
    makes whichever port the operation reads raise.
    """

    def _make(
        *,
        interactive_mode: bool = True,
        quiet: bool = False,
        inputs: t.StrSequence = (),
        password: str = "",
        error: Exception | None = None,
    ) -> p.Tests.Prompts:
        prompts = FlextCliPrompts(
            input_reader=_scripted_reader(inputs, error),
            password_reader=_scripted_reader((password,), error),
        )
        return prompts.configure(
            m.Cli.PromptRuntimeState(interactive=interactive_mode, quiet=quiet)
        )

    return _make


@pytest.fixture
def scripted_password_pair() -> Callable[[], tuple[str, str]]:
    """Provide a callable sourcing the synthetic prompt secret pair per call."""
    return lambda: (
        os.environ.get(c.Tests.PROMPT_SHORT_ENV_NAME, "short"),
        os.environ.get(c.Tests.PROMPT_VALID_ENV_NAME, "v" + "0" * 15),
    )


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Reset CLI settings before each test item."""
    _ = item
    FlextCliSettings.reset_for_testing()


def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:
    """Reset CLI settings after each test item."""
    _ = item, nextitem
    FlextCliSettings.reset_for_testing()


__all__: list[str] = ["make_prompts", "scripted_password_pair"]
