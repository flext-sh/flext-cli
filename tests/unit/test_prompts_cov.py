"""Tests for Prompts coverage - kept methods only."""

from __future__ import annotations

import builtins
from collections.abc import MutableSequence

import pytest
from flext_tests import tm

from flext_cli import FlextCliPrompts
from tests import t


class TestsCliPromptsCov:
    """Coverage tests for FlextCliPrompts."""

    def test_prompt_logs_input_when_not_test_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        prompts = FlextCliPrompts()
        captured: MutableSequence[str] = []

        def capture_info(message: str) -> None:
            captured.append(str(message))

        result = prompts.prompt("message", default="default")
        tm.ok(result)
        tm.that(bool(captured), eq=True)

    def test_read_confirmation_input_paths(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        prompts = FlextCliPrompts()
        warnings: MutableSequence[str] = []

        def capture_warning(
            *_args: t.ContainerValue,
            **_kwargs: t.ContainerValue,
        ) -> None:
            warnings.append("warn")

        tm.that(
            prompts._read_confirmation_input("m", "p", default=True).value is True,
            eq=True,
        )
        tm.that(
            prompts._read_confirmation_input("m", "p", default=False).value is True,
            eq=True,
        )
        tm.that(
            prompts._read_confirmation_input("m", "p", default=True).value is False,
            eq=True,
        )
        entries = iter(["maybe", "y"])
        tm.that(
            prompts._read_confirmation_input("m", "p", default=False).value is True,
            eq=True,
        )
        tm.that(bool(warnings), eq=True)
