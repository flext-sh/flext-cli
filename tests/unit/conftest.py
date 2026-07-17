"""Pytest configuration, prompt test doubles, and fixtures for unit tests."""

from __future__ import annotations

from typing import Self, override

import pytest

from flext_cli import FlextCliSettings
from flext_cli.services.prompts import FlextCliPrompts
from tests import m

from collections.abc import Callable

from tests import t


class TestsFlextCliScriptedPrompts(FlextCliPrompts):
    """Prompt service with typed scripting helpers for tests."""

    def override_test_env(self, *, enabled: bool | None = True) -> Self:
        """Select the explicit test-environment override."""
        self._test_env_override = enabled
        return self

    def use_input_values(self, values: t.StrSequence) -> Self:
        """Script successive prompt input values."""
        values_iter = iter(values)
        self._input_reader = lambda _prompt: next(values_iter)
        return self

    def use_input_error(self, error: Exception) -> Self:
        """Script an input-reader failure."""

        def raise_input(_prompt: str) -> str:
            raise error

        self._input_reader = raise_input
        return self

    def use_password(self, password: str) -> Self:
        """Script a password response."""
        self._password_reader = lambda _prompt: password
        return self

    def use_password_error(self, error: Exception) -> Self:
        """Script a password-reader failure."""

        def raise_password(_prompt: str) -> str:
            raise error

        self._password_reader = raise_password
        return self

    def configure_state(self, *, interactive: bool = True, quiet: bool = False) -> Self:
        """Configure the observable prompt runtime state."""
        configure(m.Cli.PromptRuntimeState(interactive=interactive, quiet=quiet))
        return self


class TestsFlextCliCaptureLogPrompts(TestsFlextCliScriptedPrompts):
    """Prompt service that captures log calls without writing to the real logger."""

    _records: list[tuple[str, str]] = m.PrivateAttr(default_factory=list)

    @property
    def records(self) -> list[tuple[str, str]]:
        """Captured log-level and message pairs."""
        return self._records

    @override
    def _log(self, log_level: str, message: str, **context: t.LogValue) -> None:
        self._records.append((log_level, message))


class TestsFlextCliFailingLogPrompts(TestsFlextCliScriptedPrompts):
    """Prompt service that fails on one selected log level."""

    _failure_level: str = m.PrivateAttr(default_factory=lambda: "")
    _failure_message: str = m.PrivateAttr(default_factory=lambda: "logger failure")

    def fail_on_log(self, *, level: str, message: str) -> Self:
        """Select the log call that raises the scripted failure."""
        self._failure_level = level
        self._failure_message = message
        return self

    @override
    def _log(self, log_level: str, message: str, **context: t.LogValue) -> None:
        if log_level == self._failure_level:
            raise ValueError(self._failure_message)
        super()._log(log_level, message, **context)


def _prompt_factory[TPrompt: TestsFlextCliScriptedPrompts](
    prompt_cls: type[TPrompt],
) -> Callable[..., TPrompt]:
    """Build a prompt-double factory that configures interactive/quiet flags."""

    def _make(*, interactive_mode: bool = True, quiet: bool = False) -> TPrompt:
        instance = prompt_cls()
        instance.configure_state(interactive=interactive_mode, quiet=quiet)
        return instance

    return _make


@pytest.fixture
def make_prompts() -> Callable[..., TestsFlextCliScriptedPrompts]:
    """Provide a factory for scripted prompt test doubles."""
    return _prompt_factory(TestsFlextCliScriptedPrompts)


@pytest.fixture
def make_capture_prompts() -> Callable[..., TestsFlextCliCaptureLogPrompts]:
    """Provide a factory for prompt doubles that capture log output."""
    return _prompt_factory(TestsFlextCliCaptureLogPrompts)


@pytest.fixture
def make_failing_prompts() -> Callable[..., TestsFlextCliFailingLogPrompts]:
    """Provide a factory for prompt doubles that can fail selected log calls."""
    return _prompt_factory(TestsFlextCliFailingLogPrompts)


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Reset CLI settings before each test item."""
    _ = item
    FlextCliSettings.reset_for_testing()


def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:
    """Reset CLI settings after each test item."""
    _ = item, nextitem
    FlextCliSettings.reset_for_testing()


__all__: list[str] = [
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliScriptedPrompts",
    "make_capture_prompts",
    "make_failing_prompts",
    "make_prompts",
]
