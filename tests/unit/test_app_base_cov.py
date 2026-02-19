from __future__ import annotations

import pytest

from flext_core import e, r

from flext_cli.app_base import FlextCliAppBase
from flext_cli.cli import UsageError as ClickUsageError
from flext_cli.settings import FlextCliSettings


class DemoApp(FlextCliAppBase):
    app_name = "demo"
    app_help = "help"
    config_class = FlextCliSettings

    def _register_commands(self) -> None:
        return None


class PathlibNameErrorApp(DemoApp):
    def _register_commands(self) -> None:
        raise NameError("pathlib is not defined")


def test_init_handles_pathlib_nameerror_in_register_commands() -> None:
    app = PathlibNameErrorApp()

    assert app is not None


def test_execute_cli_success_and_system_exit_paths(monkeypatch) -> None:
    app = DemoApp()

    def run_ok(*, args, standalone_mode):
        _ = args, standalone_mode
        return None

    app._app = run_ok
    assert app.execute_cli(["x"]).is_success

    def run_exit_zero(*, args, standalone_mode):
        _ = args, standalone_mode
        raise SystemExit(0)

    app._app = run_exit_zero
    assert app.execute_cli([]).is_success

    def run_exit_fail(*, args, standalone_mode):
        _ = args, standalone_mode
        raise SystemExit(2)

    app._app = run_exit_fail
    assert app.execute_cli([]).is_failure


def test_execute_cli_error_branches(monkeypatch) -> None:
    app = DemoApp()
    monkeypatch.setattr(app._output, "print_error", lambda _msg: r.ok(True))

    def run_nameerror(*, args, standalone_mode):
        _ = args, standalone_mode
        raise NameError("pathlib missing")

    app._app = run_nameerror
    assert app.execute_cli([]).is_failure

    def run_usage(*, args, standalone_mode):
        _ = args, standalone_mode
        raise ClickUsageError("bad usage")

    app._app = run_usage
    assert app.execute_cli([]).is_failure

    def run_value(*, args, standalone_mode):
        _ = args, standalone_mode
        raise ValueError("bad value")

    app._app = run_value
    assert app.execute_cli([]).is_failure

    class CustomBaseError(e.BaseError):
        pass

    def run_base_error(*, args, standalone_mode):
        _ = args, standalone_mode
        raise CustomBaseError("base")

    app._app = run_base_error
    assert app.execute_cli([]).is_failure

    def run_other(*, args, standalone_mode):
        _ = args, standalone_mode
        raise KeyboardInterrupt()

    app._app = run_other
    with pytest.raises(KeyboardInterrupt):
        app.execute_cli([])


def test_handle_pathlib_annotation_error_non_pathlib_raises() -> None:
    with pytest.raises(NameError):
        FlextCliAppBase._handle_pathlib_annotation_error(NameError("other"))


def test_resolve_cli_args_covers_env_path(monkeypatch) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    assert FlextCliAppBase._resolve_cli_args(None) == []

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr("sys.argv", ["prog", "--flag"])
    assert FlextCliAppBase._resolve_cli_args(None) == ["--flag"]

    resolved = FlextCliAppBase._resolve_cli_args(["a"])
    assert resolved == ["a"]


def test_execute_cli_name_error_non_pathlib_and_unexpected_exception(
    monkeypatch,
) -> None:
    app = DemoApp()

    def run_non_pathlib_nameerror(*, args, standalone_mode):
        _ = args, standalone_mode
        raise NameError("other")

    app._app = run_non_pathlib_nameerror
    with pytest.raises(NameError):
        app.execute_cli([])

    def run_assertion(*, args, standalone_mode):
        _ = args, standalone_mode
        raise AssertionError("unexpected")

    app._app = run_assertion
    with pytest.raises(AssertionError):
        app.execute_cli([])


def test_execute_cli_injects_pathlib_into_frame_globals(monkeypatch) -> None:
    app = DemoApp()

    class FakeFrame:
        def __init__(self) -> None:
            self.f_globals: dict[str, object] = {}

    fake_frame = FakeFrame()
    monkeypatch.setattr("flext_cli.app_base.inspect.currentframe", lambda: fake_frame)
    app._app = lambda *, args, standalone_mode: None

    result = app.execute_cli([])

    assert result.is_success
    assert "pathlib" in fake_frame.f_globals
