from __future__ import annotations

from pathlib import Path

from flext_core import r

from flext_cli.services.cmd import FlextCliCmd


def test_show_config_paths_failure_on_exception(monkeypatch) -> None:
    import flext_cli.services.cmd as cmd_module

    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "get_config_paths",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("paths error"))),
    )

    result = FlextCliCmd.show_config_paths()

    assert result.is_failure
    assert "paths error" in (result.error or "")


def test_validate_config_failure_on_exception(monkeypatch) -> None:
    import flext_cli.services.cmd as cmd_module

    cmd = FlextCliCmd()
    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "validate_config_structure",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("validate error"))),
    )

    result = cmd.validate_config()

    assert result.is_failure
    assert "validate error" in (result.error or "")


def test_get_config_info_failure_on_exception(monkeypatch) -> None:
    import flext_cli.services.cmd as cmd_module

    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "get_config_info",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("info error"))),
    )

    result = FlextCliCmd.get_config_info()

    assert result.is_failure
    assert "info error" in (result.error or "")


def test_set_config_value_outer_exception_path(monkeypatch) -> None:
    cmd = FlextCliCmd()

    monkeypatch.setattr(
        cmd._file_tools,
        "write_json_file",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("write exception")),
    )

    result = cmd.set_config_value("k", "v")

    assert result.is_failure
    assert "write exception" in (result.error or "")


def test_get_config_value_outer_exception_path(monkeypatch, tmp_path: Path) -> None:
    import flext_cli.services.cmd as cmd_module

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

    assert result.is_failure
    assert "read exception" in (result.error or "")


def test_show_config_failure_when_info_result_is_failure(monkeypatch) -> None:
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        FlextCliCmd, "get_config_info", staticmethod(lambda: r.fail("bad info"))
    )

    result = cmd.show_config()

    assert result.is_failure
    assert "bad info" in (result.error or "")


def test_show_config_outer_exception_path(monkeypatch) -> None:
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        FlextCliCmd,
        "get_config_info",
        staticmethod(lambda: (_ for _ in ()).throw(ValueError("show error"))),
    )

    result = cmd.show_config()

    assert result.is_failure
    assert "show error" in (result.error or "")


def test_edit_config_outer_exception_path(monkeypatch) -> None:
    import flext_cli.services.cmd as cmd_module

    monkeypatch.setattr(
        cmd_module.FlextCliServiceBase,
        "get_cli_config",
        staticmethod(
            lambda: (_ for _ in ()).throw(ValueError("config access error"))
        ),
    )

    result = FlextCliCmd().edit_config()

    assert result.is_failure
    assert "config access error" in (result.error or "")


def test_edit_config_success_logs_and_returns_ok(monkeypatch, tmp_path: Path) -> None:
    import flext_cli.services.cmd as cmd_module

    class FakeConfig:
        config_dir = tmp_path

    cli_config = tmp_path / "cli_config.json"
    cli_config.write_text('{"name": "ok"}', encoding="utf-8")

    cmd = FlextCliCmd()
    logged: dict[str, object] = {}

    monkeypatch.setattr(
        cmd_module.FlextCliServiceBase,
        "get_cli_config",
        staticmethod(lambda: FakeConfig()),
    )
    monkeypatch.setattr(
        cmd._file_tools, "read_json_file", lambda _path: r.ok({"name": "ok"})
    )
    monkeypatch.setattr(
        cmd.logger,
        "info",
        lambda message, **kwargs: logged.update({"message": message, **kwargs}),
    )

    result = cmd.edit_config()

    assert result.is_success
    assert logged["message"]
    assert "config" in logged
