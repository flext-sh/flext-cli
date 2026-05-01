"""Branch coverage tests for flext_cli._utilities.tables."""

from __future__ import annotations

import pytest

import flext_cli._utilities.tables as tables_module
from flext_cli import m
from flext_cli._utilities.tables import FlextCliUtilitiesTables


class TestsFlextCliTablesBranchCov:
    """Exercise remaining FlextCliUtilitiesTables branches."""

    def test_tables_normalize_data_invalid_input_fails(self) -> None:
        result = FlextCliUtilitiesTables.tables_normalize_data(123)
        assert result.failure
        assert "Table data invalid" in (result.error or "")

    def test_tables_normalize_data_string_row_fails(self) -> None:
        result = FlextCliUtilitiesTables.tables_normalize_data(["abc"])
        assert result.failure
        assert "Table data invalid" in (result.error or "")

    def test_tables_normalize_data_invalid_row_after_validation(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            tables_module.FlextCliUtilitiesTables.TABLE_DATA_ADAPTER,
            "validate_python",
            lambda data: [object()],
        )
        result = FlextCliUtilitiesTables.tables_normalize_data([["placeholder"]])
        assert result.failure
        assert result.error == "Table row invalid after validation"

    def test_tables_render_trims_colalign_and_normalizes_mapping_rows(self) -> None:
        settings = m.Cli.TableConfig(
            headers=("Key", "Value"),
            colalign=("left", "right", "center"),
        )
        rows = [{"Key": "a", "Value": 1}]
        result = FlextCliUtilitiesTables.tables_render(rows, settings)
        assert result.success
        assert isinstance(result.value, str)

    def test_tables_render_without_headers_uses_empty_header_list(self) -> None:
        result = FlextCliUtilitiesTables.tables_render(
            [["a", 1]],
            m.Cli.TableConfig(show_header=False, headers=("col1", "col2")),
        )
        assert result.success

    def test_tables_render_failure_returns_result_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            tables_module,
            "tabulate",
            lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("boom")),
        )
        result = FlextCliUtilitiesTables.tables_render(
            [["a", 1]],
            m.Cli.TableConfig(headers=("col1", "col2")),
        )
        assert result.failure
        assert "boom" in (result.error or "")


__all__: list[str] = ["TestsFlextCliTablesBranchCov"]
