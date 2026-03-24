"""Command coverage tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_core import r
from flext_tests import tm

import flext_cli.services.cmd as cmd_module
from flext_cli import FlextCliCmd, m
from tests import t


def test_show_config_paths_failure_on_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "get_config_paths",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("paths error"))),
    )
    result = FlextCliCmd.show_config_paths()
    tm.fail(result)
    tm.that((result.error or ""), has="paths error")


def test_validate_config_failure_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "validate_config_structure",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("validate error"))),
    )
    result = cmd.validate_config()
    tm.fail(result)
    tm.that((result.error or ""), has="validate error")


def test_get_config_info_failure_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "get_config_info",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("info error"))),
    )
    result = FlextCliCmd.get_config_info()
    tm.fail(result)
    tm.that((result.error or ""), has="info error")


def test_set_config_value_outer_exception_path(monkeypatch: pytest.MonkeyPatch) -> None:
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        cmd._file_tools,
        "write_json_file",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("write exception")),
    )
    result = cmd.set_config_value("k", "v")
    tm.fail(result)
    tm.that((result.error or ""), has="write exception")


def test_get_config_value_outer_exception_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:

    class FakeConfig:
        config_dir = tmp_path

    (tmp_path / "cli_config.json").write_text('{"x": 1}', encoding="utf-8")
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        cmd_module.FlextCliServiceBase,
        "get_cli_config",
        staticmethod(lambda: FakeConfig()),
    )
    monkeypatch.setattr(
        cmd._file_tools,
        "read_json_file",
        lambda _path: (_ for _ in ()).throw(ValueError("read exception")),
    )
    result = cmd.get_config_value("x")
    tm.fail(result)
    tm.that((result.error or ""), has="read exception")


def test_show_config_failure_when_info_result_is_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        FlextCliCmd,
        "get_config_info",
        staticmethod(lambda: r[m.Cli.ConfigSnapshot].fail("bad info")),
    )
    result = cmd.show_config()
    tm.fail(result)
    tm.that((result.error or ""), has="bad info")


def test_show_config_outer_exception_path(monkeypatch: pytest.MonkeyPatch) -> None:
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        FlextCliCmd,
        "get_config_info",
        staticmethod(lambda: (_ for _ in ()).throw(ValueError("show error"))),
    )
    result = cmd.show_config()
    tm.fail(result)
    tm.that((result.error or ""), has="show error")


def test_edit_config_outer_exception_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cmd_module.FlextCliServiceBase,
        "get_cli_config",
        staticmethod(lambda: (_ for _ in ()).throw(ValueError("config access error"))),
    )
    result = FlextCliCmd().edit_config()
    tm.fail(result)
    tm.that((result.error or ""), has="config access error")


def test_edit_config_success_logs_and_returns_ok(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:

    class FakeConfig:
        config_dir = tmp_path

    cli_config = tmp_path / "cli_config.json"
    cli_config.write_text('{"name": "ok"}', encoding="utf-8")
    cmd = FlextCliCmd()
    logged: t.ContainerMapping = {}
    monkeypatch.setattr(
        cmd_module.FlextCliServiceBase,
        "get_cli_config",
        staticmethod(lambda: FakeConfig()),
    )
    monkeypatch.setattr(
        cmd._file_tools,
        "read_json_file",
        lambda _path: r.ok({"name": "ok"}),
    )
    monkeypatch.setattr(
        cmd.logger,
        "info",
        lambda message, **kwargs: logged.update({"message": message, **kwargs}),
    )
    result = cmd.edit_config()
    tm.ok(result)
    tm.that(logged, has="message")
    tm.that(logged, has="config")
