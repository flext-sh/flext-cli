"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Generator,
)

import pytest
from flext_core import FlextSettings

from flext_cli import FlextCliSettings
from tests import t
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
        **_kwargs: t.JsonValue,
    ) -> TestsFlextCliScriptedPrompts:
        return prompt_type().configure_state(
            interactive=interactive_mode,
            quiet=quiet,
        )

    return _make


__all__: list[str] = [
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliScriptedPrompts",
    "make_prompts",
]


@pytest.fixture(autouse=True)
def reset_config_singleton(request: pytest.FixtureRequest) -> Generator[None]:
    """Reset FlextCliSettings singleton before and after each test.

    This ensures test isolation and prevents one test from contaminating
    the state for other tests.
    """
    FlextCliSettings._reset_instance()
    FlextSettings.reset_for_testing()
    yield
    FlextCliSettings._reset_instance()
    FlextSettings.reset_for_testing()
