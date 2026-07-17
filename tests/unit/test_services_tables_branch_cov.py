"""Behavioral tests for the public table-formatting contract of FlextCli.

Exercises the observable contract of ``FlextCli.format_table`` (returns
``r[str]``) and ``FlextCli.show_table`` (renders to the console) through the
public facade only. No private attributes, no internal-collaborator spying.
"""

from __future__ import annotations


import pytest

from flext_cli import cli, m
from tests import c
from flext_tests import tm

from flext_cli import t


class TestsFlextCliServicesTablesBranchCov:
    """Public-contract behavior of format_table / show_table."""

    @pytest.fixture
    def mapping_payload(self) -> t.Cli.TableDataSource:
        """Return a key/value mapping table payload."""
        return {"a": 1, "b": 2}

    @pytest.fixture
    def rows_payload(self) -> t.Cli.TableDataSource:
        """Return a header-plus-rows list payload."""
        return [["col1", "col2"], ["a", "b"]]

    # ---- format_table: success contract (returns r[str]) ----

    def test_format_table_default_config_succeeds_with_rendered_content(
        self, mapping_payload: t.Cli.TableDataSource
    ) -> None:
        """Verify that format table default config succeeds with rendered content."""
        result = cli.format_table(mapping_payload)

        tm.ok(result)
        rendered = result.unwrap()
        tm.that(rendered, has="a")
        tm.that(rendered, has="1")
        tm.that(rendered, has="b")
        tm.that(rendered, has="2")

    def test_format_table_list_payload_renders_all_cells(
        self, rows_payload: t.Cli.TableDataSource
    ) -> None:
        """Verify that format table list payload renders all cells."""
        result = cli.format_table(rows_payload)

        tm.ok(result)
        rendered = result.unwrap()
        tm.that(rendered, has="col1")
        tm.that(rendered, has="col2")
        tm.that(rendered, has="a")
        tm.that(rendered, has="b")

    @pytest.mark.parametrize(
        ("table_format", "expected_marker"),
        [(c.Cli.TabularFormat.GRID, "+"), (c.Cli.TabularFormat.PIPE, "|")],
    )
    def test_format_table_honors_requested_format_via_settings(
        self,
        mapping_payload: t.Cli.TableDataSource,
        table_format: c.Cli.TabularFormat,
        expected_marker: str,
    ) -> None:
        """Verify that format table honors requested format via settings."""
        settings = m.Cli.TableConfig(table_format=table_format)

        result = cli.format_table(mapping_payload, settings=settings)

        tm.ok(result)
        tm.that(result.unwrap(), has=expected_marker)

    def test_format_table_is_idempotent_for_equal_input(
        self, mapping_payload: t.Cli.TableDataSource
    ) -> None:
        """Verify that format table is idempotent for equal input."""
        first = cli.format_table(mapping_payload)
        second = cli.format_table(mapping_payload)

        tm.ok(first)
        tm.ok(second)
        tm.that(first.unwrap(), eq=second.unwrap())

    # ---- format_table: failure contract ----

    @pytest.mark.parametrize("bad_format", ["invalid", "not-a-format", ""])
    def test_format_table_rejects_invalid_format_string(
        self, mapping_payload: t.Cli.TableDataSource, bad_format: str
    ) -> None:
        """Verify that format table rejects invalid format string."""
        result = cli.format_table(mapping_payload, table_format=bad_format)

        tm.fail(result)
        tm.that((result.error or ""), has=c.Cli.OUTPUT_TABLE_CONFIG_INVALID)

    # ---- show_table: console rendering contract ----

    def test_show_table_prints_rendered_table(
        self, mapping_payload: t.Cli.TableDataSource, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that show table prints rendered table."""
        cli.show_table(mapping_payload)

        captured = capsys.readouterr().out
        tm.that(captured, has="a")
        tm.that(captured, has="1")

    def test_show_table_prints_title_above_table(
        self, mapping_payload: t.Cli.TableDataSource, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that show table prints title above table."""
        cli.show_table(mapping_payload, title="My Title")

        captured = capsys.readouterr().out
        tm.that(captured, has="My Title")
        tm.that(captured, has="a")
        tm.that(captured, has="1")

    def test_show_table_prints_list_payload(
        self, rows_payload: t.Cli.TableDataSource, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that show table prints list payload."""
        cli.show_table(rows_payload)

        captured = capsys.readouterr().out
        tm.that(captured, has="col1")
        tm.that(captured, has="a")

    def test_show_table_emits_config_error_on_invalid_format(
        self, mapping_payload: t.Cli.TableDataSource, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that show table emits config error on invalid format."""
        cli.show_table(mapping_payload, table_format="invalid")

        captured = capsys.readouterr().out
        tm.that(captured, has=c.Cli.OUTPUT_TABLE_CONFIG_INVALID)


__all__: list[str] = ["TestsFlextCliServicesTablesBranchCov"]
