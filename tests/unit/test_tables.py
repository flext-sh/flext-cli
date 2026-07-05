"""Behavioral tests for the public CLI table helpers.

Exercises the observable contract of ``cli.format_table`` and ``cli.show_table``
only: the ``r[str]`` outcome, rendered content, header handling, failure paths,
invariants (idempotence, empty data), and console ordering. No implementation
detail (private attrs, internal collaborators) is touched.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_cli import cli
from tests.constants import c

if TYPE_CHECKING:
    from flext_cli import t


class TestsFlextCliTables:
    """Regression coverage for the public table helpers."""

    def test_format_table_accepts_single_mapping_and_sequence_kwargs(self) -> None:
        """A single mapping plus list-based settings kwargs render successfully."""
        table: str = tm.ok(
            cli.format_table(
                {"status": "ok", "count": 2},
                headers=["Field", "Value"],
                colalign=["left", "right"],
                table_format=c.Cli.TabularFormat.GRID,
            ),
        )
        tm.that(table, has=["Field", "status", "ok"])

    def test_format_table_supports_headerless_mapping_rows(self) -> None:
        """Headerless rendering emits values but suppresses the column keys."""
        table: str = tm.ok(
            cli.format_table(
                [{"identifier": "row-1", "display_name": "Alpha"}],
                show_header=False,
                table_format=c.Cli.TabularFormat.PLAIN,
            ),
        )
        tm.that(table, has=["row-1", "Alpha"])
        tm.that("identifier" in table, eq=False)

    @pytest.mark.parametrize(
        "table_format",
        [
            c.Cli.TabularFormat.TABLE,
            c.Cli.TabularFormat.GRID,
            c.Cli.TabularFormat.PLAIN,
            c.Cli.TabularFormat.SIMPLE,
            c.Cli.TabularFormat.PSQL,
        ],
    )
    def test_format_table_renders_row_values_across_formats(
        self,
        table_format: c.Cli.TabularFormat,
    ) -> None:
        """Every supported tabular format renders the underlying row values."""
        table: str = tm.ok(
            cli.format_table(
                [{"name": "Alice", "status": "active"}],
                table_format=table_format,
            ),
        )
        tm.that(table, has=["Alice", "active"])

    def test_format_table_renders_multiple_rows_in_order(self) -> None:
        """Multiple rows appear in their input order in the rendered output."""
        table: str = tm.ok(
            cli.format_table(
                [{"n": "first"}, {"n": "second"}, {"n": "third"}],
                table_format=c.Cli.TabularFormat.PLAIN,
            ),
        )
        tm.that(table, has=["first", "second", "third"])
        tm.that(
            table.index("first") < table.index("second") < table.index("third"),
            eq=True,
        )

    @pytest.mark.parametrize("empty_data", [[], {}])
    def test_format_table_returns_empty_string_for_empty_data(
        self,
        empty_data: t.Cli.TableDataSource,
    ) -> None:
        """Empty input is a success carrying an empty rendered table."""
        table: str = tm.ok(cli.format_table(empty_data))
        tm.that(table, eq="")

    def test_format_table_is_idempotent_for_identical_input(self) -> None:
        """Rendering the same data twice yields byte-identical output."""
        rows = [{"name": "Alice", "status": "active"}]
        first: str = tm.ok(cli.format_table(rows, table_format=c.Cli.TabularFormat.GRID))
        second: str = tm.ok(
            cli.format_table(rows, table_format=c.Cli.TabularFormat.GRID),
        )
        tm.that(first == second, eq=True)

    def test_format_table_fails_on_unknown_configuration_kwarg(self) -> None:
        """An unrecognized config kwarg surfaces a validation failure, not a render."""
        error: str = tm.fail(
            cli.format_table([{"name": "Alice"}], bogus_kwarg=1),
        )
        tm.that(error, has=["table configuration", "bogus_kwarg"])

    def test_show_table_prints_title_before_rendered_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """show_table prints the title ahead of the rendered table body."""
        cli.show_table(
            {"service": "cli", "state": "ready"},
            headers=["Field", "Value"],
            title="Current State",
        )
        output = capsys.readouterr().out
        tm.that(output, has=["Current State", "service"])
        tm.that(output.index("Current State") < output.index("service"), eq=True)

    def test_show_table_reports_configuration_failure_to_console(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """An invalid configuration is surfaced on the console rather than raising."""
        cli.show_table([{"name": "Alice"}], bogus_kwarg=1)
        output = capsys.readouterr().out
        tm.that(output, has=["bogus_kwarg"])
