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


def _prompt_factory[TPrompt: TestsFlextCliScriptedPrompts](
    prompt_cls: type[TPrompt],
) -> Callable[..., TPrompt]:
    """Build a prompt-double factory that configures interactive/quiet flags."""

    def _make(
        *,
        interactive_mode: bool = True,
        quiet: bool = False,
    ) -> TPrompt:
        instance = prompt_cls()
        instance.configure_state(interactive=interactive_mode, quiet=quiet)
        return instance

    return _make


@pytest.fixture
def make_prompts() -> Callable[..., TestsFlextCliScriptedPrompts]:
    """Factory fixture for scripted prompt test doubles."""
    return _prompt_factory(TestsFlextCliScriptedPrompts)


@pytest.fixture
def make_capture_prompts() -> Callable[..., TestsFlextCliCaptureLogPrompts]:
    """Factory fixture for prompt doubles that capture log output."""
    return _prompt_factory(TestsFlextCliCaptureLogPrompts)


@pytest.fixture
def make_failing_prompts() -> Callable[..., TestsFlextCliFailingLogPrompts]:
    """Factory fixture for prompt doubles that can fail selected log calls."""
    return _prompt_factory(TestsFlextCliFailingLogPrompts)


@pytest.fixture(autouse=True)
def reset_config_singleton() -> Generator[None]:
    """Reset cli.settings singleton before and after each test.

    Settings are resolved via ``FlextCliSettings.fetch_global()`` per access
    (no cache), so a single ``reset_for_testing`` is sufficient.
    """
    cli.settings.reset_for_testing()
    yield
    cli.settings.reset_for_testing()


__all__: list[str] = [
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliScriptedPrompts",
    "make_capture_prompts",
    "make_failing_prompts",
    "make_prompts",
    "reset_settings",
]
