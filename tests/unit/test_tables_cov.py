"""Coverage tests for _utilities/tables.py.

Targets: tables_normalize_mapping_row, tables_normalize_sequence_row,
         tables_resolve_config, tables_normalize_data, tables_render.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.constants import c
from tests.models import m
from tests.typings import t
from tests.utilities import u


class TestsFlextCliTableUtilsCov:
    """Coverage tests for u.Cli."""

    # ── tables_normalize_mapping_row ──────────────────────────────────

    def test_tables_normalize_mapping_row_simple(self) -> None:
        row = {"a": 1, "b": "hello"}
        result = u.Cli.tables_normalize_mapping_row(row)
        assert result["a"] == 1
        assert result["b"] == "hello"

    def test_tables_normalize_mapping_row_none_value(self) -> None:
        row = {"key": None}
        result = u.Cli.tables_normalize_mapping_row(row)
        assert isinstance(result, dict)

    # ── tables_normalize_sequence_row ─────────────────────────────────

    def test_tables_normalize_sequence_row_simple(self) -> None:
        row = [1, "text", True]
        result = u.Cli.tables_normalize_sequence_row(row)
        assert len(result) == 3

    def test_tables_normalize_sequence_row_empty(self) -> None:
        result = u.Cli.tables_normalize_sequence_row([])
        assert result == []

    # ── tables_resolve_config ─────────────────────────────────────────

    def test_tables_resolve_config_no_args(self) -> None:
        result = u.Cli.tables_resolve_config()
        assert result.success
        assert isinstance(result.value, m.Cli.TableConfig)

    def test_tables_resolve_config_with_model(self) -> None:
        config = m.Cli.TableConfig()
        result = u.Cli.tables_resolve_config(config)
        assert result.success
        assert result.value is config

    def test_tables_resolve_config_with_kwargs(self) -> None:
        result = u.Cli.tables_resolve_config(table_format=c.Cli.TabularFormat.PLAIN)
        assert result.success

    def test_tables_resolve_config_invalid_kwarg(self) -> None:
        result = u.Cli.tables_resolve_config(not_a_field="oops")
        assert result.failure

    # ── tables_normalize_data ─────────────────────────────────────────

    def test_tables_normalize_data_mapping(self) -> None:
        data: t.JsonMapping = {"key": "val", "num": 42}
        result = u.Cli.tables_normalize_data(data)
        assert result.success
        rows = list(result.value)
        assert len(rows) == 2

    def test_tables_normalize_data_list_of_dicts(self) -> None:
        data = [{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}]
        result = u.Cli.tables_normalize_data(data)
        assert result.success

    def test_tables_normalize_data_list_of_lists(self) -> None:
        data = [["a", "b"], ["c", "d"]]
        result = u.Cli.tables_normalize_data(data)
        assert result.success

    def test_tables_normalize_data_empty_list(self) -> None:
        result = u.Cli.tables_normalize_data([])
        assert result.success
        assert list(result.value) == []

    # ── tables_render ─────────────────────────────────────────────────

    def test_tables_render_mapping_rows(self) -> None:
        config = m.Cli.TableConfig()
        rows: list[t.JsonMapping] = [
            {"Key": "a", "Value": 1},
            {"Key": "b", "Value": 2},
        ]
        result = u.Cli.tables_render(rows, config)
        assert result.success
        assert isinstance(result.value, str)

    def test_tables_render_sequence_rows(self) -> None:
        config = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.PLAIN)
        rows: list[list[t.JsonValue]] = [["a", 1], ["b", 2]]
        result = u.Cli.tables_render(rows, config)
        assert result.success

    def test_tables_render_empty_rows(self) -> None:
        config = m.Cli.TableConfig()
        result = u.Cli.tables_render([], config)
        assert result.success


__all__: list[str] = ["TestsFlextCliTableUtilsCov"]
