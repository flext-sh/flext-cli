"""Tests for CLI table formatting and display helpers."""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCliTables


class TestsCliTables:
    """Regression coverage for public table helpers."""

    def test_format_table_accepts_single_mapping_and_sequence_kwargs(self) -> None:
        """Single mappings and list-based config kwargs must be accepted."""
        result = FlextCliTables.format_table(
            {"status": "ok", "count": 2},
            headers=["Field", "Value"],
            colalign=["left", "right"],
            table_format="grid",
        )
        tm.that(result.success, eq=True)
        table = result.value or ""
        tm.that("Field" in table, eq=True)
        tm.that("status" in table, eq=True)
        tm.that("ok" in table, eq=True)

    def test_format_table_supports_headerless_mapping_rows(self) -> None:
        """Headerless rendering must work for row sequences from examples."""
        result = FlextCliTables.format_table(
            [{"identifier": "row-1", "display_name": "Alpha"}],
            show_header=False,
            table_format="plain",
        )
        tm.that(result.success, eq=True)
        table = result.value or ""
        tm.that("row-1" in table, eq=True)
        tm.that("Alpha" in table, eq=True)
        tm.that("identifier" in table, eq=False)

    def test_format_table_accepts_public_table_alias(self) -> None:
        """The public 'table' format alias must resolve to the default backend."""
        result = FlextCliTables.format_table(
            [{"name": "Alice", "status": "active"}],
            table_format="table",
        )
        tm.that(result.success, eq=True)
        table = result.value or ""
        tm.that("Alice" in table, eq=True)
        tm.that("active" in table, eq=True)

    def test_show_table_prints_title_before_rendered_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """show_table must print the title before the rendered table body."""
        FlextCliTables.show_table(
            {"service": "cli", "state": "ready"},
            headers=["Field", "Value"],
            title="Current State",
        )
        captured = capsys.readouterr()
        output = captured.out
        tm.that("Current State" in output, eq=True)
        tm.that("service" in output, eq=True)
        tm.that(output.index("Current State") < output.index("service"), eq=True)
