"""Tests for Prompts."""

from __future__ import annotations

import builtins
from collections.abc import Sequence
from typing import Never

import pytest
from flext_tests import tm

from flext_cli import FlextCliPrompts


def test_prompt_confirmation_handles_exception_from_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)

    def explode_record(_value: str) -> Never:
        msg = "record boom"
        raise ValueError(msg)

    monkeypatch.setattr(
        prompts,
        "_record",
        explode_record,
    )
    result = prompts.prompt_confirmation("continue?")
    tm.fail(result)


def test_prompt_choice_covers_required_default_and_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    missing_default = prompts.prompt_choice("pick", ["a", "b"], default=None)
    tm.fail(missing_default)

    def explode_choice_record(_value: str) -> Never:
        msg = "choice boom"
        raise ValueError(msg)

    monkeypatch.setattr(
        prompts,
        "_record",
        explode_choice_record,
    )
    exploded = prompts.prompt_choice("pick", ["a"], default="a")
    tm.fail(exploded)


def test_prompt_logs_input_when_not_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
    captured: list[str] = []

    def capture_info(message: str) -> None:
        captured.append(str(message))

    monkeypatch.setattr(prompts, "_is_test_env", lambda: False)
    monkeypatch.setattr(prompts.logger, "info", capture_info)
    monkeypatch.setattr(builtins, "input", lambda _msg="": "typed")
    result = prompts.prompt("message", default="default")
    tm.ok(result)
    tm.that(bool(captured), eq=True)


def test_read_confirmation_input_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    warnings: list[str] = []

    def capture_warning(*_args: object, **_kwargs: object) -> None:
        warnings.append("warn")

    monkeypatch.setattr(prompts.logger, "warning", capture_warning)
    monkeypatch.setattr(builtins, "input", lambda _msg="": "")
    tm.that(
        prompts._read_confirmation_input("m", "p", default=True).value is True, eq=True
    )
    monkeypatch.setattr(builtins, "input", lambda _msg="": "yes")
    tm.that(
        prompts._read_confirmation_input("m", "p", default=False).value is True, eq=True
    )
    monkeypatch.setattr(builtins, "input", lambda _msg="": "no")
    tm.that(
        prompts._read_confirmation_input("m", "p", default=True).value is False, eq=True
    )
    entries = iter(["maybe", "y"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries))
    tm.that(
        prompts._read_confirmation_input("m", "p", default=False).value is True, eq=True
    )
    tm.that(bool(warnings), eq=True)


def test_read_selection_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    entries_empty = iter(["", "1"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries_empty))
    tm.that(prompts._read_selection(["a", "b"]).value, eq="a")
    monkeypatch.setattr(builtins, "input", lambda _msg="": "1")
    tm.that(prompts._read_selection(["a", "b"]).value, eq="a")
    entries = iter(["bad", "2"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries))
    tm.that(prompts._read_selection(["a", "b"]).value, eq="b")
    monkeypatch.setattr(
        builtins, "input", lambda _msg="": (_ for _ in ()).throw(KeyboardInterrupt())
    )
    tm.fail(prompts._read_selection(["a"]))
    monkeypatch.setattr(
        builtins, "input", lambda _msg="": (_ for _ in ()).throw(EOFError())
    )
    tm.fail(prompts._read_selection(["a"]))


def test_select_from_options_logs_successful_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
    logs: list[str] = []

    def capture_info(msg: str) -> None:
        logs.append(str(msg))

    class _SuccessfulSelection:
        is_success: bool = True
        value: str = "b"

    def successful_selection(_values: Sequence[str]) -> _SuccessfulSelection:
        return _SuccessfulSelection()

    monkeypatch.setattr(prompts.logger, "info", capture_info)
    monkeypatch.setattr(
        prompts,
        "_read_selection",
        successful_selection,
    )
    result = prompts.select_from_options(["a", "b"], "pick one")
    tm.ok(result)
    tm.that(bool(logs), eq=True)


def test_print_status_exception_path(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)

    def explode_info(_msg: str) -> Never:
        msg = "log boom"
        raise ValueError(msg)

    def swallow_exception(*_args: object, **_kwargs: object) -> None:
        return

    monkeypatch.setattr(
        prompts.logger,
        "info",
        explode_info,
    )
    monkeypatch.setattr(prompts.logger, "exception", swallow_exception)
    result = prompts.print_status("hi")
    tm.fail(result)
