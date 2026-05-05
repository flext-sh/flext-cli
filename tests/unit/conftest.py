"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Generator,
)

import pytest
from flext_tests import reset_settings

from flext_cli import cli
from tests.helpers._impl import (
    TestsFlextCliCaptureLogPrompts,
    TestsFlextCliFailingLogPrompts,
    TestsFlextCliScriptedPrompts,
)


@pytest.fixture
def make_prompts() -> Callable[..., TestsFlextCliScriptedPrompts]:
    """Factory fixture for scripted prompt test doubles."""

    def _make(
        prompt_type: type[TestsFlextCliScriptedPrompts] = TestsFlextCliScriptedPrompts,
        *,
        interactive_mode: bool = True,
        quiet: bool = False,
    ) -> TestsFlextCliScriptedPrompts:
        return prompt_type().configure_state(
            interactive=interactive_mode,
            quiet=quiet,
        )

    return _make


@pytest.fixture(autouse=True)
def reset_config_singleton() -> Generator[None]:
    """Reset cli.settings singleton before and after each test.

    Settings are now resolved via ``FlextCliSettings.fetch_global()`` per
    access (no cache), so a single ``reset_for_testing`` is sufficient.
    """
    cli.settings.reset_for_testing()
    yield
    cli.settings.reset_for_testing()


__all__: list[str] = [
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliScriptedPrompts",
    "make_prompts",
    "reset_settings",
]
