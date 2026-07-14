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

from tests import c
from tests import m
from tests import u
from flext_tests import tm

from tests import t



class TestsFlextCliTables:
    """Observable-behavior tests for the public table-helper contract."""

    # ── tables_normalize_mapping_row ──────────────────────────────────

    def test_normalize_mapping_row_preserves_keys_and_json_values(self) -> None:
        """Preserve mapping keys and JSON-native values."""
        row: t.Cli.TableMappingRow = {"a": 1, "b": "hello"}
        result = u.Cli.tables_normalize_mapping_row(row)
        tm.that(result, eq={"a": 1, "b": "hello"})

    def test_normalize_mapping_row_preserves_json_null(self) -> None:
        """Preserve JSON null instead of inventing an empty string."""
        result = u.Cli.tables_normalize_mapping_row({"key": None})
        tm.that(result, eq={"key": None})

    def test_normalize_mapping_row_is_idempotent_on_json_values(self) -> None:
        """Remain idempotent for already normalized JSON values."""
        row: t.Cli.TableMappingRow = {"a": 1, "b": "x"}
        once = u.Cli.tables_normalize_mapping_row(row)
        twice = u.Cli.tables_normalize_mapping_row(once)
        tm.that(once, eq=twice)

    # ── tables_normalize_sequence_row ─────────────────────────────────

    def test_normalize_sequence_row_preserves_length_and_order(self) -> None:
        """Preserve sequence length, order, and JSON-native values."""
        result = u.Cli.tables_normalize_sequence_row([1, "text", True])
        tm.that(result, eq=[1, "text", True])

    def test_normalize_sequence_row_empty_yields_empty_list(self) -> None:
        """Return an empty list for an empty row."""
        tm.that(u.Cli.tables_normalize_sequence_row([]), eq=[])

    # ── tables_resolve_config ─────────────────────────────────────────

    def test_resolve_config_no_args_returns_default_model(self) -> None:
        """Return a default table configuration when no input is supplied."""
        result = u.Cli.tables_resolve_config()
        tm.ok(result)
        tm.that(result.unwrap(), is_=m.Cli.TableConfig)

    def test_resolve_config_returns_same_instance_when_only_model_given(self) -> None:
        """Reuse the validated configuration instance without rebuilding it."""
        config = m.Cli.TableConfig()
        result = u.Cli.tables_resolve_config(config)
        tm.that(result.unwrap() is config, eq=True)

    def test_resolve_config_applies_kwarg_override(self) -> None:
        """Apply an explicit keyword override to the default configuration."""
        result = u.Cli.tables_resolve_config(table_format=c.Cli.TabularFormat.PLAIN)
        tm.ok(result)
        tm.that(result.unwrap().table_format, eq=c.Cli.TabularFormat.PLAIN)

    def test_resolve_config_merges_model_with_kwargs(self) -> None:
        """Merge explicit overrides with a validated configuration model."""
        base = m.Cli.TableConfig(title="orig")
        result = u.Cli.tables_resolve_config(
            base, table_format=c.Cli.TabularFormat.PLAIN
        )
        resolved = result.unwrap()
        tm.that(resolved.title, eq="orig")
        tm.that(resolved.table_format, eq=c.Cli.TabularFormat.PLAIN)

    def test_resolve_config_invalid_kwarg_fails_with_config_message(self) -> None:
        """Reject an unknown configuration field with context."""
        result = u.Cli.tables_resolve_config(not_a_field="oops")
        tm.fail(result)
        tm.that((result.error or ""), has="Invalid table configuration")

    # ── tables_normalize_data ─────────────────────────────────────────

    def test_normalize_data_mapping_becomes_key_value_rows(self) -> None:
        """Convert a mapping into ordered key and value rows."""
        data: t.JsonMapping = {"key": "val", "num": 42}
        rows = list(u.Cli.tables_normalize_data(data).unwrap())
        tm.that(rows, eq=[{"Key": "key", "Value": "val"}, {"Key": "num", "Value": 42}])

    def test_normalize_data_list_of_dicts_preserves_rows(self) -> None:
        """Preserve mapping rows supplied as a list."""
        data = [{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}]
        rows = list(u.Cli.tables_normalize_data(data).unwrap())
        tm.that(rows, eq=data)

    def test_normalize_data_list_of_lists_preserves_rows(self) -> None:
        """Preserve sequence rows supplied as a list."""
        rows = list(u.Cli.tables_normalize_data([["a", "b"], ["c", "d"]]).unwrap())
        tm.that(rows, eq=[["a", "b"], ["c", "d"]])

    def test_normalize_data_empty_list_yields_no_rows(self) -> None:
        """Return no normalized rows for an empty data source."""
        tm.that(list(u.Cli.tables_normalize_data([]).unwrap()), eq=[])

    # NOTE: The malformed-input failure branch of ``tables_normalize_data``
    # (OUTPUT_TABLE_DATA_INVALID / OUTPUT_TABLE_ROW_INVALID) is only reachable by
    # passing values outside the declared ``t.Cli.TableDataSource`` contract
    # (e.g. a list of bare ints). Driving it would require a typing-suppression
    # comment, so it is intentionally left uncovered rather than faked. The
    # invalid-config error path is covered above via ``tables_resolve_config``.

    # ── tables_render ─────────────────────────────────────────────────

    def test_render_mapping_rows_includes_cell_values(self) -> None:
        """Render every observable value from mapping rows."""
        config = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.PLAIN)
        rows: list[t.JsonMapping] = [{"Name": "x", "Age": 1}, {"Name": "y", "Age": 2}]
        rendered = u.Cli.tables_render(rows, config).unwrap()
        tm.that(rendered, has="x")
        tm.that(rendered, has="y")

    def test_render_sequence_rows_includes_cell_values(self) -> None:
        """Render every observable value from sequence rows."""
        config = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.PLAIN)
        rows: list[list[t.JsonValue]] = [["a", 1], ["b", 2]]
        rendered = u.Cli.tables_render(rows, config).unwrap()
        tm.that(rendered, has="a")
        tm.that(rendered, has="b")

    def test_render_empty_rows_yields_string(self) -> None:
        """Return a string when rendering an empty row collection."""
        config = m.Cli.TableConfig()
        result = u.Cli.tables_render([], config)
        tm.ok(result)
        tm.that(result.unwrap(), is_=str)

    @pytest.mark.parametrize(
        "table_format",
        [
            c.Cli.TabularFormat.PLAIN,
            c.Cli.TabularFormat.SIMPLE,
            c.Cli.TabularFormat.GRID,
        ],
    )
    def test_render_succeeds_across_formats(
        self, table_format: c.Cli.TabularFormat
    ) -> None:
        """Render successfully through each supported table format."""
        config = m.Cli.TableConfig(table_format=table_format)
        rows: list[t.JsonMapping] = [{"K": "v"}]
        result = u.Cli.tables_render(rows, config)
        tm.ok(result)
        tm.that(result.unwrap(), is_=str)


__all__: list[str] = ["TestsFlextCliTables"]
