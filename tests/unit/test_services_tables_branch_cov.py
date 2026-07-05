"""Behavioral tests for the public table-formatting contract of FlextCli.

Exercises the observable contract of ``FlextCli.format_table`` (returns
``r[str]``) and ``FlextCli.show_table`` (renders to the console) through the
public facade only. No private attributes, no internal-collaborator spying.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_cli import cli, m
from tests.constants import c

if TYPE_CHECKING:
    from flext_cli import t


class TestsFlextCliServicesTablesBranchCov:
    """Public-contract behavior of format_table / show_table."""

    @pytest.fixture
    def mapping_payload(self) -> t.Cli.TableDataSource:
        """A key/value mapping table payload."""
        return {"a": 1, "b": 2}

    @pytest.fixture
    def rows_payload(self) -> t.Cli.TableDataSource:
        """A header-plus-rows list payload."""
        return [["col1", "col2"], ["a", "b"]]

    # ---- format_table: success contract (returns r[str]) ----

    def test_format_table_default_config_succeeds_with_rendered_content(
        self,
        mapping_payload: t.Cli.TableDataSource,
    ) -> None:
        result = cli.format_table(mapping_payload)

        assert result.success
        rendered = result.unwrap()
        assert "a" in rendered
        assert "1" in rendered
        assert "b" in rendered
        assert "2" in rendered

    def test_format_table_list_payload_renders_all_cells(
        self,
        rows_payload: t.Cli.TableDataSource,
    ) -> None:
        result = cli.format_table(rows_payload)

        assert result.success
        rendered = result.unwrap()
        assert "col1" in rendered
        assert "col2" in rendered
        assert "a" in rendered
        assert "b" in rendered

    @pytest.mark.parametrize(
        ("table_format", "expected_marker"),
        [
            (c.Cli.TabularFormat.GRID, "+"),
            (c.Cli.TabularFormat.PIPE, "|"),
        ],
    )
    def test_format_table_honors_requested_format_via_settings(
        self,
        mapping_payload: t.Cli.TableDataSource,
        table_format: c.Cli.TabularFormat,
        expected_marker: str,
    ) -> None:
        settings = m.Cli.TableConfig(table_format=table_format)

        result = cli.format_table(mapping_payload, settings=settings)

        assert result.success
        assert expected_marker in result.unwrap()

    def test_format_table_is_idempotent_for_equal_input(
        self,
        mapping_payload: t.Cli.TableDataSource,
    ) -> None:
        first = cli.format_table(mapping_payload)
        second = cli.format_table(mapping_payload)

        assert first.success
        assert second.success
        assert first.unwrap() == second.unwrap()

    # ---- format_table: failure contract ----

    @pytest.mark.parametrize("bad_format", ["invalid", "not-a-format", ""])
    def test_format_table_rejects_invalid_format_string(
        self,
        mapping_payload: t.Cli.TableDataSource,
        bad_format: str,
    ) -> None:
        result = cli.format_table(mapping_payload, table_format=bad_format)

        assert result.failure
        assert c.Cli.OUTPUT_TABLE_CONFIG_INVALID in (result.error or "")

    # ---- show_table: console rendering contract ----

    def test_show_table_prints_rendered_table(
        self,
        mapping_payload: t.Cli.TableDataSource,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table(mapping_payload)

        captured = capsys.readouterr().out
        assert "a" in captured
        assert "1" in captured

    def test_show_table_prints_title_above_table(
        self,
        mapping_payload: t.Cli.TableDataSource,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table(mapping_payload, title="My Title")

        captured = capsys.readouterr().out
        assert "My Title" in captured
        assert "a" in captured
        assert "1" in captured

    def test_show_table_prints_list_payload(
        self,
        rows_payload: t.Cli.TableDataSource,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table(rows_payload)

        captured = capsys.readouterr().out
        assert "col1" in captured
        assert "a" in captured

    def test_show_table_emits_config_error_on_invalid_format(
        self,
        mapping_payload: t.Cli.TableDataSource,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table(mapping_payload, table_format="invalid")

        captured = capsys.readouterr().out
        assert c.Cli.OUTPUT_TABLE_CONFIG_INVALID in captured


__all__: list[str] = ["TestsFlextCliServicesTablesBranchCov"]
