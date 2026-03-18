"""Tests for Prompts."""

from __future__ import annotations

import builtins

import pytest
from flext_tests import tm

from flext_cli import FlextCliPrompts


def test_prompt_confirmation_handles_exception_from_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    monkeypatch.setattr(
        prompts,
        "_record",
        lambda _value: (_ for _ in ()).throw(ValueError("record boom")),
    )
    result = prompts.prompt_confirmation("continue?")
    tm.fail(result)


def test_prompt_choice_covers_required_default_and_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    missing_default = prompts.prompt_choice("pick", ["a", "b"], default=None)
    tm.fail(missing_default)
    monkeypatch.setattr(
        prompts,
        "_record",
        lambda _value: (_ for _ in ()).throw(ValueError("choice boom")),
    )
    exploded = prompts.prompt_choice("pick", ["a"], default="a")
    tm.fail(exploded)


def test_prompt_logs_input_when_not_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
    captured: list[str] = []
    monkeypatch.setattr(prompts, "_is_test_env", lambda: False)
    monkeypatch.setattr(
        prompts.logger, "info", lambda message: captured.append(str(message))
    )
    monkeypatch.setattr(builtins, "input", lambda _msg="": "typed")
    result = prompts.prompt("message", default="default")
    tm.ok(result)
    tm.that(captured, eq=True)


def test_read_confirmation_input_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    warnings: list[str] = []
    monkeypatch.setattr(
        prompts.logger, "warning", lambda *args, **kwargs: warnings.append("warn")
    )
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
    tm.that(warnings, eq=True)


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
    monkeypatch.setattr(prompts.logger, "info", lambda msg: logs.append(str(msg)))
    monkeypatch.setattr(
        prompts,
        "_read_selection",
        lambda _values: type("X", (), {"is_success": True, "value": "b"})(),
    )
    result = prompts.select_from_options(["a", "b"], "pick one")
    tm.ok(result)
    tm.that(logs, eq=True)


def test_print_status_exception_path(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    monkeypatch.setattr(
        prompts.logger,
        "info",
        lambda _msg: (_ for _ in ()).throw(ValueError("log boom")),
    )
    monkeypatch.setattr(prompts.logger, "exception", lambda *args, **kwargs: None)
    result = prompts.print_status("hi")
    tm.fail(result)
