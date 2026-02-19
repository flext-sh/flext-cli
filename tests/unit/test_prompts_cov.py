from __future__ import annotations

import builtins

from flext_cli.services.prompts import FlextCliPrompts


def test_prompt_confirmation_handles_exception_from_record(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    monkeypatch.setattr(
        prompts,
        "_record",
        lambda _value: (_ for _ in ()).throw(RuntimeError("record boom")),
    )

    result = prompts.prompt_confirmation("continue?")

    assert result.is_failure


def test_prompt_choice_covers_required_default_and_exception(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)

    missing_default = prompts.prompt_choice("pick", ["a", "b"], default=None)
    assert missing_default.is_failure

    monkeypatch.setattr(
        prompts,
        "_record",
        lambda _value: (_ for _ in ()).throw(RuntimeError("choice boom")),
    )
    exploded = prompts.prompt_choice("pick", ["a"], default="a")
    assert exploded.is_failure


def test_prompt_logs_input_when_not_test_env(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
    captured: list[str] = []

    monkeypatch.setattr(prompts, "_is_test_env", lambda: False)
    monkeypatch.setattr(
        prompts.logger, "info", lambda message: captured.append(str(message))
    )
    monkeypatch.setattr(builtins, "input", lambda _msg="": "typed")

    result = prompts.prompt("message", default="default")

    assert result.is_success
    assert captured


def test_read_confirmation_input_paths(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    warnings: list[str] = []
    monkeypatch.setattr(
        prompts.logger, "warning", lambda *args, **kwargs: warnings.append("warn")
    )

    monkeypatch.setattr(builtins, "input", lambda _msg="": "")
    assert prompts._read_confirmation_input("m", "p", default=True).value is True

    monkeypatch.setattr(builtins, "input", lambda _msg="": "yes")
    assert prompts._read_confirmation_input("m", "p", default=False).value is True

    monkeypatch.setattr(builtins, "input", lambda _msg="": "no")
    assert prompts._read_confirmation_input("m", "p", default=True).value is False

    entries = iter(["maybe", "y"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries))
    assert prompts._read_confirmation_input("m", "p", default=False).value is True
    assert warnings


def test_read_selection_paths(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)

    entries_empty = iter(["", "1"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries_empty))
    assert prompts._read_selection(["a", "b"]).value == "a"

    monkeypatch.setattr(builtins, "input", lambda _msg="": "1")
    assert prompts._read_selection(["a", "b"]).value == "a"

    entries = iter(["bad", "2"])
    monkeypatch.setattr(builtins, "input", lambda _msg="": next(entries))
    assert prompts._read_selection(["a", "b"]).value == "b"

    monkeypatch.setattr(
        builtins,
        "input",
        lambda _msg="": (_ for _ in ()).throw(KeyboardInterrupt()),
    )
    assert prompts._read_selection(["a"]).is_failure

    monkeypatch.setattr(
        builtins,
        "input",
        lambda _msg="": (_ for _ in ()).throw(EOFError()),
    )
    assert prompts._read_selection(["a"]).is_failure


def test_select_from_options_logs_successful_selection(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True, quiet=False)
    logs: list[str] = []
    monkeypatch.setattr(prompts.logger, "info", lambda msg: logs.append(str(msg)))
    monkeypatch.setattr(
        prompts,
        "_read_selection",
        lambda _values: type("X", (), {"is_success": True, "value": "b"})(),
    )

    result = prompts.select_from_options(["a", "b"], "pick one")

    assert result.is_success
    assert logs


def test_print_status_exception_path(monkeypatch) -> None:
    prompts = FlextCliPrompts(interactive_mode=True)
    monkeypatch.setattr(
        prompts.logger,
        "info",
        lambda _msg: (_ for _ in ()).throw(RuntimeError("log boom")),
    )
    monkeypatch.setattr(prompts.logger, "exception", lambda *args, **kwargs: None)

    result = prompts.print_status("hi")

    assert result.is_failure
