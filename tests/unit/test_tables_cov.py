"""Behavioral tests for the ``u.Cli.tables_*`` public table helpers.

Contract under test (from ``flext_cli._utilities.tables``):
    tables_normalize_mapping_row, tables_normalize_sequence_row,
    tables_resolve_config, tables_normalize_data, tables_render.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.constants import c
from tests.models import m
from tests.utilities import u

if TYPE_CHECKING:
    from tests.typings import t


class TestsFlextCliTables:
    """Observable-behavior tests for the public table-helper contract."""

    # ── tables_normalize_mapping_row ──────────────────────────────────

    def test_normalize_mapping_row_preserves_keys_and_json_values(self) -> None:
        row: t.Cli.TableMappingRow = {"a": 1, "b": "hello"}
        result = u.Cli.tables_normalize_mapping_row(row)
        assert result == {"a": 1, "b": "hello"}

    def test_normalize_mapping_row_renders_none_as_empty_string(self) -> None:
        result = u.Cli.tables_normalize_mapping_row({"key": None})
        assert result == {"key": ""}

    def test_normalize_mapping_row_is_idempotent_on_json_values(self) -> None:
        row: t.Cli.TableMappingRow = {"a": 1, "b": "x"}
        once = u.Cli.tables_normalize_mapping_row(row)
        twice = u.Cli.tables_normalize_mapping_row(once)
        assert once == twice

    # ── tables_normalize_sequence_row ─────────────────────────────────

    def test_normalize_sequence_row_preserves_length_and_order(self) -> None:
        result = u.Cli.tables_normalize_sequence_row([1, "text", True])
        assert result == [1, "text", True]

    def test_normalize_sequence_row_empty_yields_empty_list(self) -> None:
        assert u.Cli.tables_normalize_sequence_row([]) == []

    # ── tables_resolve_config ─────────────────────────────────────────

    def test_resolve_config_no_args_returns_default_model(self) -> None:
        result = u.Cli.tables_resolve_config()
        assert result.success
        assert isinstance(result.unwrap(), m.Cli.TableConfig)

    def test_resolve_config_returns_same_instance_when_only_model_given(self) -> None:
        config = m.Cli.TableConfig()
        result = u.Cli.tables_resolve_config(config)
        assert result.unwrap() is config

    def test_resolve_config_applies_kwarg_override(self) -> None:
        result = u.Cli.tables_resolve_config(table_format=c.Cli.TabularFormat.PLAIN)
        assert result.success
        assert result.unwrap().table_format == c.Cli.TabularFormat.PLAIN

    def test_resolve_config_merges_model_with_kwargs(self) -> None:
        base = m.Cli.TableConfig(title="orig")
        result = u.Cli.tables_resolve_config(
            base, table_format=c.Cli.TabularFormat.PLAIN
        )
        resolved = result.unwrap()
        assert resolved.title == "orig"
        assert resolved.table_format == c.Cli.TabularFormat.PLAIN

    def test_resolve_config_invalid_kwarg_fails_with_config_message(self) -> None:
        result = u.Cli.tables_resolve_config(not_a_field="oops")
        assert result.failure
        assert "Invalid table configuration" in (result.error or "")

    # ── tables_normalize_data ─────────────────────────────────────────

    def test_normalize_data_mapping_becomes_key_value_rows(self) -> None:
        data: t.JsonMapping = {"key": "val", "num": 42}
        rows = list(u.Cli.tables_normalize_data(data).unwrap())
        assert rows == [
            {"Key": "key", "Value": "val"},
            {"Key": "num", "Value": 42},
        ]

    def test_normalize_data_list_of_dicts_preserves_rows(self) -> None:
        data = [{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}]
        rows = list(u.Cli.tables_normalize_data(data).unwrap())
        assert rows == data

    def test_normalize_data_list_of_lists_preserves_rows(self) -> None:
        rows = list(u.Cli.tables_normalize_data([["a", "b"], ["c", "d"]]).unwrap())
        assert rows == [["a", "b"], ["c", "d"]]

    def test_normalize_data_empty_list_yields_no_rows(self) -> None:
        assert list(u.Cli.tables_normalize_data([]).unwrap()) == []

    # NOTE: The malformed-input failure branch of ``tables_normalize_data``
    # (OUTPUT_TABLE_DATA_INVALID / OUTPUT_TABLE_ROW_INVALID) is only reachable by
    # passing values outside the declared ``t.Cli.TableDataSource`` contract
    # (e.g. a list of bare ints). Driving it would require a typing-suppression
    # comment, so it is intentionally left uncovered rather than faked. The
    # invalid-config error path is covered above via ``tables_resolve_config``.

    # ── tables_render ─────────────────────────────────────────────────

    def test_render_mapping_rows_includes_cell_values(self) -> None:
        config = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.PLAIN)
        rows: list[t.JsonMapping] = [{"Name": "x", "Age": 1}, {"Name": "y", "Age": 2}]
        rendered = u.Cli.tables_render(rows, config).unwrap()
        assert "x" in rendered
        assert "y" in rendered

    def test_render_sequence_rows_includes_cell_values(self) -> None:
        config = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.PLAIN)
        rows: list[list[t.JsonValue]] = [["a", 1], ["b", 2]]
        rendered = u.Cli.tables_render(rows, config).unwrap()
        assert "a" in rendered
        assert "b" in rendered

    def test_render_empty_rows_yields_string(self) -> None:
        config = m.Cli.TableConfig()
        result = u.Cli.tables_render([], config)
        assert result.success
        assert isinstance(result.unwrap(), str)

    @pytest.mark.parametrize(
        "table_format",
        [
            c.Cli.TabularFormat.PLAIN,
            c.Cli.TabularFormat.SIMPLE,
            c.Cli.TabularFormat.GRID,
        ],
    )
    def test_render_succeeds_across_formats(
        self,
        table_format: c.Cli.TabularFormat,
    ) -> None:
        config = m.Cli.TableConfig(table_format=table_format)
        rows: list[t.JsonMapping] = [{"K": "v"}]
        result = u.Cli.tables_render(rows, config)
        assert result.success
        assert isinstance(result.unwrap(), str)


__all__: list[str] = ["TestsFlextCliTables"]
