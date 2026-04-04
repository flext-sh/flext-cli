"""Tests for Prompts coverage - kept methods only."""

from __future__ import annotations

import builtins
from collections.abc import MutableSequence

import pytest
from flext_tests import tm

from flext_cli import FlextCliPrompts
from tests import t


def test_prompt_logs_input_when_not_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts()
    captured: MutableSequence[str] = []

    def capture_info(message: str) -> None:
        captured.append(str(message))

    monkeypatch.setattr(prompts, "_is_test_env", lambda: False)
    monkeypatch.setattr(prompts.logger, "info", capture_info)
    monkeypatch.setattr(builtins, "input", lambda _msg="": "typed")
    result = prompts.prompt("message", default="default")
    tm.ok(result)
    tm.that(bool(captured), eq=True)


def test_read_confirmation_input_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts()
    warnings: MutableSequence[str] = []

    def capture_warning(
        *_args: t.ContainerValue,
        **_kwargs: t.ContainerValue,
    ) -> None:
        warnings.append("warn")

    monkeypatch.setattr(prompts.logger, "warning", capture_warning)
    monkeypatch.setattr(builtins, "input", lambda _msg="": "")
    tm.that(
        prompts._read_confirmation_input("m", "p", default=True).value is True,
        eq=True,
    )
    monkeypatch.setattr(builtins, "input", lambda _msg="": "yes")
    tm.that(
        prompts._read_confirmation_input("m", "p", default=False).value is True,
        eq=True,
    )
    monkeypatch.setattr(builtins, "input", lambda _msg="": "no")
    tm.that(
        prompts._read_confirmation_input("m", "p", default=True).value is False,
        eq=True,
    )
    entries = iter(["maybe", "y"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries))
    tm.that(
        prompts._read_confirmation_input("m", "p", default=False).value is True,
        eq=True,
    )
    tm.that(bool(warnings), eq=True)
