"""Command coverage tests."""

from __future__ import annotations

import pytest
from flext_core import r
from flext_tests import tm

import flext_cli.services.cmd as cmd_module
from flext_cli import FlextCliCmd, m
from tests import t


def test_show_config_paths_failure_on_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test show_config_paths static utility failure path.

    Note: show_config_paths was deleted from FlextCliCmd, but the underlying
    utility u.Cli.ConfigOps.get_config_paths still exists. This tests
    validate_config which wraps it.
    """
    cmd = FlextCliCmd()
    monkeypatch.setattr(
        cmd_module.FlextCliUtilities.Cli.ConfigOps,
        "validate_config_structure",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("paths error"))),
    )
    result = cmd.validate_config()
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
