"""Branch coverage tests for flext_cli.services.tables."""

from __future__ import annotations

import pytest

import flext_cli.services.tables as tables_service_module
from flext_cli import c, m
from flext_cli.services.tables import FlextCliTables
from flext_core import r


class TestsFlextCliServicesTablesBranchCov:
    """Exercise failure and title branches for FlextCliTables."""

    @staticmethod
    def _ok_config() -> object:
        return r[m.Cli.TableConfig].ok(m.Cli.TableConfig())

    def test_format_table_config_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_resolve_config",
            lambda settings=None, **kwargs: r[m.Cli.TableConfig].fail("bad-config"),
        )
        result = FlextCliTables.format_table({"a": 1})
        assert result.failure
        assert result.error == "bad-config"

    def test_format_table_normalize_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_resolve_config",
            lambda settings=None, **kwargs: self._ok_config(),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_normalize_data",
            lambda data: r[tuple[object, ...]].fail("bad-data"),
        )
        result = FlextCliTables.format_table({"a": 1})
        assert result.failure
        assert result.error == "bad-data"

    def test_show_table_config_failure_emits_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        printed: list[tuple[str, str | None]] = []

        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_resolve_config",
            lambda settings=None, **kwargs: r[m.Cli.TableConfig].fail("bad-config"),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "output_table_error",
            lambda error_message: (f"ERR:{error_message}", "red"),
        )
        monkeypatch.setattr(
            tables_service_module.FlextCliFormatters,
            "print",
            lambda message, style=None: printed.append((message, style)),
        )
        FlextCliTables.show_table({"a": 1})
        assert printed == [("ERR:bad-config", "red")]

    def test_show_table_normalize_failure_emits_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        printed: list[tuple[str, str | None]] = []

        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_resolve_config",
            lambda settings=None, **kwargs: self._ok_config(),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_normalize_data",
            lambda data: r[tuple[object, ...]].fail("bad-data"),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "output_table_error",
            lambda error_message: (f"ERR:{error_message}", "red"),
        )
        monkeypatch.setattr(
            tables_service_module.FlextCliFormatters,
            "print",
            lambda message, style=None: printed.append((message, style)),
        )
        FlextCliTables.show_table({"a": 1})
        assert printed == [("ERR:bad-data", "red")]

    def test_show_table_success_with_title_prints_title_and_table(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        printed: list[tuple[str, str | None]] = []
        config = m.Cli.TableConfig(title="My Title")

        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_resolve_config",
            lambda settings=None, **kwargs: r[m.Cli.TableConfig].ok(config),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_normalize_data",
            lambda data: r[tuple[object, ...]].ok((["row"],)),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_render",
            lambda rows, config_final: r[str].ok("TABLE"),
        )
        monkeypatch.setattr(
            tables_service_module.FlextCliFormatters,
            "print",
            lambda message, style=None: printed.append((message, style)),
        )
        FlextCliTables.show_table({"a": 1})
        assert printed == [
            ("My Title", c.Cli.MessageStyles.BOLD),
            ("TABLE", None),
        ]

    def test_show_table_render_failure_emits_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        printed: list[tuple[str, str | None]] = []

        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_resolve_config",
            lambda settings=None, **kwargs: self._ok_config(),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_normalize_data",
            lambda data: r[tuple[object, ...]].ok((["row"],)),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "tables_render",
            lambda rows, config_final: r[str].fail("bad-render"),
        )
        monkeypatch.setattr(
            tables_service_module.u.Cli,
            "output_table_error",
            lambda error_message: (f"ERR:{error_message}", "red"),
        )
        monkeypatch.setattr(
            tables_service_module.FlextCliFormatters,
            "print",
            lambda message, style=None: printed.append((message, style)),
        )
        FlextCliTables.show_table({"a": 1})
        assert printed == [("ERR:bad-render", "red")]


__all__: list[str] = ["TestsFlextCliServicesTablesBranchCov"]
