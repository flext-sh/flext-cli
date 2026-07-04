"""Tests for CLI table formatting and display helpers."""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import cli
from tests.constants import c


class TestsFlextCliTables:
    """Regression coverage for public table helpers."""

    def test_format_table_accepts_single_mapping_and_sequence_kwargs(self) -> None:
        """Single mappings and list-based settings kwargs must be accepted."""
        table: str = tm.ok(
            cli.format_table(
                {"status": "ok", "count": 2},
                headers=["Field", "Value"],
                colalign=["left", "right"],
                table_format=c.Cli.TabularFormat.GRID,
            )
        )
        tm.that(table, has=["Field", "status", "ok"])

    def test_format_table_supports_headerless_mapping_rows(self) -> None:
        """Headerless rendering must work for row sequences from examples."""
        table: str = tm.ok(
            cli.format_table(
                [{"identifier": "row-1", "display_name": "Alpha"}],
                show_header=False,
                table_format=c.Cli.TabularFormat.PLAIN,
            )
        )
        tm.that(table, has=["row-1", "Alpha"])
        tm.that("identifier" in table, eq=False)

    def test_format_table_accepts_public_table_alias(self) -> None:
        """The public 'table' format alias must resolve to the default backend."""
        table: str = tm.ok(
            cli.format_table(
                [{"name": "Alice", "status": "active"}],
                table_format=c.Cli.TabularFormat.TABLE,
            )
        )
        tm.that(table, has=["Alice", "active"])

    def test_show_table_prints_title_before_rendered_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """show_table must print the title before the rendered table body."""
        cli.show_table(
            {"service": "cli", "state": "ready"},
            headers=["Field", "Value"],
            title="Current State",
        )
        output = capsys.readouterr().out
        tm.that(output, has=["Current State", "service"])
        tm.that(output.index("Current State") < output.index("service"), eq=True)
