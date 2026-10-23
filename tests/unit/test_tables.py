"""Behavioral tests for the public CLI table helpers.

Exercises the observable contract of ``cli.format_table`` and ``cli.show_table``
only: the ``r[str]`` outcome, rendered content, header handling, failure paths,
invariants (idempotence, empty data), and console ordering. No implementation
detail (private attrs, internal collaborators) is touched.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pytest

from flext_cli import cli
from tests import c, m, tm

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliTables:
    """Regression coverage for the public table helpers."""

    @staticmethod
    @pytest.mark.parametrize(
        ("data", "cells"),
        [
            pytest.param(
                {"name": "Alice", "age": 30},
                ("name", "Alice", "age", "30"),
                id="single-record-return-type",
            ),
            pytest.param(
                {"name": "Alice", "age": 30},
                ("name", "Alice", "age", "30"),
                id="single-record-cells",
            ),
            pytest.param(
                [{"col": "val1"}, {"col": "val2"}],
                ("col", "val1", "val2"),
                id="mapping-rows",
            ),
            pytest.param({"a": 1, "b": 2}, ("a", "1", "b", "2"), id="mapping"),
            pytest.param(
                [["col1", "col2"], ["a", "b"]],
                ("col1", "col2", "a", "b"),
                id="header-and-value-rows",
            ),
        ],
    )
    def test_format_table_renders_input_cells(
        data: t.Cli.TableDataSource,
        cells: t.StrTuple,
    ) -> None:
        """All previously separate payload shapes return text containing every cell."""
        rendered = tm.ok(cli.format_table(data))
        tm.that(rendered, is_=str)
        tm.that(rendered, has=cells)

    @staticmethod
    def test_format_table_accepts_single_mapping_and_sequence_kwargs() -> None:
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

    @staticmethod
    def test_format_table_supports_headerless_mapping_rows() -> None:
        """Headerless rendering emits values but suppresses the column keys."""
        table: str = tm.ok(
            cli.format_table(
                [{"identifier": "row-1", "display_name": "Alpha"}],
                show_header=False,
                table_format=c.Cli.TabularFormat.PLAIN,
            ),
        )
        tm.that(table, has=["row-1", "Alpha"])
        tm.fail("identifier" in table)

    @staticmethod
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

    @staticmethod
    def test_format_table_renders_multiple_rows_in_order() -> None:
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

    @staticmethod
    @pytest.mark.parametrize(
        "empty_data",
        [
            pytest.param([], id="table-empty-list"),
            pytest.param({}, id="table-empty-mapping"),
            pytest.param([], id="service-empty-list"),
            pytest.param({}, id="service-empty-mapping"),
        ],
    )
    def test_format_table_returns_empty_string_for_empty_data(
        empty_data: t.Cli.TableDataSource,
    ) -> None:
        """Empty input is a success carrying an empty rendered table."""
        table: str = tm.ok(cli.format_table(empty_data))
        tm.that(table, eq="")

    @staticmethod
    @pytest.mark.parametrize(
        ("rows", "table_format"),
        [
            pytest.param(
                [{"name": "Alice", "status": "active"}],
                c.Cli.TabularFormat.GRID,
                id="explicit-grid-rows",
            ),
            pytest.param({"name": "Alice", "age": 30}, None, id="single-record"),
            pytest.param({"a": 1, "b": 2}, None, id="mapping"),
        ],
    )
    def test_format_table_is_idempotent_for_identical_input(
        rows: t.Cli.TableDataSource,
        table_format: c.Cli.TabularFormat | None,
    ) -> None:
        """Rendering the same data twice yields byte-identical output."""
        config = (
            m.Cli.TableConfig(table_format=table_format)
            if table_format is not None
            else m.Cli.TableConfig()
        )
        first = tm.ok(cli.format_table(rows, config))
        second = tm.ok(cli.format_table(rows, config))
        tm.ok(first == second)

    @staticmethod
    @pytest.mark.parametrize(
        ("data", "table_format", "marker", "route"),
        [
            pytest.param({"a": 1, "b": 2}, c.Cli.TabularFormat.GRID, "+", "settings"),
            pytest.param({"a": 1, "b": 2}, c.Cli.TabularFormat.PIPE, "|", "settings"),
            pytest.param(
                {"name": "Alice", "age": 30}, c.Cli.TabularFormat.GRID, "+", "model"
            ),
            pytest.param(
                {"name": "Alice", "age": 30}, c.Cli.TabularFormat.PIPE, "|", "model"
            ),
            pytest.param(
                {"name": "Alice", "age": 30}, c.Cli.TabularFormat.RST, "=", "model"
            ),
        ],
    )
    def test_format_table_honors_requested_format(
        data: t.Cli.TableDataSource,
        table_format: c.Cli.TabularFormat,
        marker: str,
        route: Literal["settings", "model"],
    ) -> None:
        """Both configuration routes preserve data and select the requested style."""
        config = m.Cli.TableConfig(table_format=table_format)
        rendered = tm.ok(
            cli.format_table(data, settings=config)
            if route == "settings"
            else cli.format_table(data, config)
        )
        tm.that(rendered, has=marker)
        baseline = m.Cli.TableConfig()
        if baseline.table_format != table_format:
            tm.that(rendered, ne=tm.ok(cli.format_table(data, baseline)))
        if route == "model":
            tm.that(rendered, has="Alice")

    @staticmethod
    def test_format_table_accepts_config_via_keyword_argument() -> None:
        """A keyword field and an explicit config model produce the same output."""
        data = {"name": "Alice", "age": 30}
        config = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.GRID)
        via_kwarg = tm.ok(cli.format_table(data, table_format=config.table_format))
        tm.that(via_kwarg, eq=tm.ok(cli.format_table(data, config)))

    @staticmethod
    def test_format_table_title_is_not_embedded_in_returned_string() -> None:
        """The returned table body excludes its display-only title."""
        config = m.Cli.TableConfig(title="My Report")
        rendered = tm.ok(cli.format_table({"name": "Alice", "age": 30}, config))
        tm.that(rendered, lacks=config.title)

    @staticmethod
    def test_format_table_custom_headers_appear_in_output() -> None:
        """Supplied headers replace the configured default labels."""
        headers = ["K", "V"]
        rendered = tm.ok(cli.format_table({"a": 1}, m.Cli.TableConfig(headers=headers)))
        tm.that(rendered, has=headers)

    @staticmethod
    @pytest.mark.parametrize("bad_format", ["invalid", "not-a-format", ""])
    def test_format_table_rejects_invalid_format_string(bad_format: str) -> None:
        """Invalid requested formats retain the public configuration diagnostic."""
        result = cli.format_table({"a": 1, "b": 2}, table_format=bad_format)
        tm.fail(result, has=c.Cli.OUTPUT_TABLE_CONFIG_INVALID)

    @staticmethod
    def test_format_table_fails_on_unknown_configuration_kwarg() -> None:
        """An unrecognized config kwarg surfaces a validation failure, not a render."""
        error: str = tm.fail(cli.format_table([{"name": "Alice"}], bogus_kwarg=1))
        tm.that(error, has=["table configuration", "bogus_kwarg"])

    @staticmethod
    def test_show_table_prints_title_before_rendered_table(
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
        tm.ok(output.index("Current State") < output.index("service"))

    @staticmethod
    def test_show_table_reports_configuration_failure_to_console(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """An invalid configuration is surfaced on the console rather than raising."""
        cli.show_table([{"name": "Alice"}], bogus_kwarg=1)
        output = capsys.readouterr().out
        tm.that(output, has=["bogus_kwarg"])

    @staticmethod
    @pytest.mark.parametrize(
        ("data", "title", "route", "cells"),
        [
            pytest.param(
                {"name": "Alice", "age": 30}, None, "keyword", (), id="return-none"
            ),
            pytest.param(
                [{"col": "val1"}, {"col": "val2"}],
                None,
                "keyword",
                ("val1", "val2"),
                id="mapping-row-output",
            ),
            pytest.param(
                {"name": "Alice", "age": 30},
                "Quarterly Numbers",
                "model",
                ("Quarterly Numbers", "Alice"),
                id="configured-title",
            ),
            pytest.param(
                {"a": 1, "b": 2}, None, "keyword", ("a", "1"), id="mapping-output"
            ),
            pytest.param(
                {"a": 1, "b": 2},
                "My Title",
                "keyword",
                ("My Title", "a", "1"),
                id="keyword-title",
            ),
            pytest.param(
                [["col1", "col2"], ["a", "b"]],
                None,
                "keyword",
                ("col1", "a"),
                id="header-and-value-output",
            ),
        ],
    )
    def test_show_table_returns_none_and_renders_cells(
        capsys: pytest.CaptureFixture[str],
        data: t.Cli.TableDataSource,
        title: str | None,
        route: Literal["keyword", "model"],
        cells: t.StrTuple,
    ) -> None:
        """Each original display case uses one real console consumer workflow."""
        if route == "model":
            result = cli.show_table(data, m.Cli.TableConfig(title=title))
        elif title is not None:
            result = cli.show_table(data, title=title)
        else:
            result = cli.show_table(data)
        tm.that(result, none=True)
        output = capsys.readouterr().out
        for cell in cells:
            tm.that(output, has=cell)

    @staticmethod
    def test_show_table_emits_config_error_on_invalid_format(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """An invalid format is reported through the same public console boundary."""
        cli.show_table({"a": 1, "b": 2}, table_format="invalid")
        tm.that(capsys.readouterr().out, has=c.Cli.OUTPUT_TABLE_CONFIG_INVALID)
