"""Behavioral tests for the public table-rendering contract.

Exercises the observable contract of ``cli.format_table`` (returns ``r[str]``)
and ``cli.show_table`` (returns ``None``, writes to stdout) through the public
``FlextCli`` facade only. No private attribute/method access, no internal
collaborator spying.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import c, cli, m, t


class TestsFlextCliServicesTablesCov:
    """Behavioral contract for FlextCli table formatting and display."""

    # ── fixtures ──────────────────────────────────────────────────────

    @pytest.fixture
    def single_record(self) -> t.Cli.TableDataSource:
        """One mapping rendered as a Key/Value table."""
        return {"name": "Alice", "age": 30}

    @pytest.fixture
    def record_rows(self) -> t.Cli.TableDataSource:
        """A list of homogeneous mappings rendered as a column table."""
        return [{"col": "val1"}, {"col": "val2"}]

    # ── format_table: return contract ─────────────────────────────────

    def test_format_table_returns_successful_result_with_str_value(
        self, single_record: t.Cli.TableDataSource
    ) -> None:
        # Act
        result = cli.format_table(single_record)

        # Assert — fallible op returns a successful r[str]
        assert result.success
        assert isinstance(result.unwrap(), str)

    def test_format_table_dict_renders_keys_and_values(
        self, single_record: t.Cli.TableDataSource
    ) -> None:
        # Act
        rendered = cli.format_table(single_record).unwrap()

        # Assert — every key and value appears in the rendered output
        assert "name" in rendered
        assert "Alice" in rendered
        assert "age" in rendered
        assert "30" in rendered

    def test_format_table_list_of_dicts_renders_every_row(
        self, record_rows: t.Cli.TableDataSource
    ) -> None:
        # Act
        rendered = cli.format_table(record_rows).unwrap()

        # Assert — column header plus each row value present
        assert "col" in rendered
        assert "val1" in rendered
        assert "val2" in rendered

    # ── format_table: edge cases / invariants ─────────────────────────

    @pytest.mark.parametrize(
        "empty_source",
        [
            pytest.param({}, id="empty-dict"),
            pytest.param([], id="empty-list"),
        ],
    )
    def test_format_table_empty_source_yields_empty_string(
        self, empty_source: t.Cli.TableDataSource
    ) -> None:
        # Act
        result = cli.format_table(empty_source)

        # Assert — empty input is valid and renders to an empty table
        assert result.success
        assert result.unwrap() == ""

    def test_format_table_is_idempotent_for_equal_input(
        self, single_record: t.Cli.TableDataSource
    ) -> None:
        # Act — same input rendered twice
        first = cli.format_table(single_record).unwrap()
        second = cli.format_table(single_record).unwrap()

        # Assert — deterministic rendering
        assert first == second

    # ── format_table: configuration behavior ──────────────────────────

    def test_format_table_title_is_not_embedded_in_returned_string(
        self, single_record: t.Cli.TableDataSource
    ) -> None:
        # Arrange — title is a display concern, not part of the formatted table
        config = m.Cli.TableConfig(title="My Report")

        # Act
        rendered = cli.format_table(single_record, config).unwrap()

        # Assert — format_table returns the table body only, without the title
        assert "My Report" not in rendered

    @pytest.mark.parametrize(
        "table_format",
        [
            pytest.param(c.Cli.TabularFormat.GRID, id="grid"),
            pytest.param(c.Cli.TabularFormat.PIPE, id="pipe"),
            pytest.param(c.Cli.TabularFormat.RST, id="rst"),
        ],
    )
    def test_format_table_format_changes_rendered_output(
        self,
        single_record: t.Cli.TableDataSource,
        table_format: c.Cli.TabularFormat,
    ) -> None:
        # Arrange
        default_rendered = cli.format_table(single_record).unwrap()
        config = m.Cli.TableConfig(table_format=table_format)

        # Act
        styled_rendered = cli.format_table(single_record, config).unwrap()

        # Assert — a non-default table format produces distinct output that
        # still carries the underlying data
        assert styled_rendered != default_rendered
        assert "Alice" in styled_rendered

    def test_format_table_accepts_config_via_keyword_argument(
        self, single_record: t.Cli.TableDataSource
    ) -> None:
        # Act — config field supplied as a kwarg is equivalent to the model
        via_kwarg = cli.format_table(
            single_record, table_format=c.Cli.TabularFormat.GRID
        ).unwrap()
        via_model = cli.format_table(
            single_record, m.Cli.TableConfig(table_format=c.Cli.TabularFormat.GRID)
        ).unwrap()

        # Assert
        assert via_kwarg == via_model

    def test_format_table_custom_headers_appear_in_output(self) -> None:
        # Arrange
        config = m.Cli.TableConfig(headers=["K", "V"])

        # Act
        rendered = cli.format_table({"a": 1}, config).unwrap()

        # Assert — supplied headers override default Key/Value labels
        assert "K" in rendered
        assert "V" in rendered

    # ── show_table: return + observable output ────────────────────────

    def test_show_table_returns_none(
        self, single_record: t.Cli.TableDataSource
    ) -> None:
        # Act / Assert — display is a side-effecting command returning None
        assert cli.show_table(single_record) is None

    def test_show_table_writes_data_to_stdout(
        self,
        record_rows: t.Cli.TableDataSource,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        cli.show_table(record_rows)

        # Assert — rendered rows reach the console
        out = capsys.readouterr().out
        assert "val1" in out
        assert "val2" in out

    def test_show_table_prints_title_when_configured(
        self,
        single_record: t.Cli.TableDataSource,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Arrange
        config = m.Cli.TableConfig(title="Quarterly Numbers")

        # Act
        cli.show_table(single_record, config)

        # Assert — the title is emitted alongside the table body
        out = capsys.readouterr().out
        assert "Quarterly Numbers" in out
        assert "Alice" in out


__all__: list[str] = ["TestsFlextCliServicesTablesCov"]
