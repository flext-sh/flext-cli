"""Implementation of test helpers - factories, validation, scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self, override

from tests import m, t

from flext_cli import FlextCliPrompts


class TestsFlextCliScriptedPrompts(FlextCliPrompts):
    """Prompt service with typed scripting helpers for tests."""

    def use_input_values(self, values: t.StrSequence) -> Self:
        values_iter = iter(values)
        self._input_reader = lambda _prompt: next(values_iter)
        return self

    def use_input_error(self, error: Exception) -> Self:
        def raise_input(_prompt: str) -> str:
            raise error

        self._input_reader = raise_input
        return self

    def use_password(self, password: str) -> Self:
        self._password_reader = lambda _prompt: password
        return self

    def use_password_error(self, error: Exception) -> Self:
        def raise_password(_prompt: str) -> str:
            raise error

        self._password_reader = raise_password
        return self

    def configure_state(
        self,
        *,
        interactive: bool = True,
        quiet: bool = False,
    ) -> Self:
        return self.configure(
            m.Cli.PromptRuntimeState(
                interactive=interactive,
                quiet=quiet,
            ),
        )


class TestsFlextCliCaptureLogPrompts(TestsFlextCliScriptedPrompts):
    """Prompt service that captures log calls without writing to the real logger."""

    _records: list[tuple[str, str]] = m.PrivateAttr(default_factory=list)

    @property
    def records(self) -> list[tuple[str, str]]:
        return self._records

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.LogValue,
    ) -> None:
        self._records.append((log_level, message))


class TestsFlextCliFailingLogPrompts(TestsFlextCliScriptedPrompts):
    """Prompt service that fails on one selected log level."""

    _failure_level: str = m.PrivateAttr(default_factory=lambda: "")
    _failure_message: str = m.PrivateAttr(default_factory=lambda: "logger failure")

    def fail_on_log(self, *, level: str, message: str) -> Self:
        self._failure_level = level
        self._failure_message = message
        return self

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.LogValue,
    ) -> None:
        if log_level == self._failure_level:
            raise ValueError(self._failure_message)
        super()._log(log_level, message, **context)


__all__: list[str] = [
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliScriptedPrompts",
]
