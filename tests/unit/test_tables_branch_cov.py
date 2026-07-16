"""Behavioral contract tests for the ``u.Cli.tables_*`` public surface."""

from __future__ import annotations

import pytest

from tests import c
from tests import m
from tests import t
from tests import u
from flext_tests import tm


class TestsFlextCliTablesBranchCov:
    """Assert the observable contract of the ``u.Cli`` table helpers."""

    @pytest.fixture
    def two_column_config(self) -> p.Cli.TableConfig:
        """Return a minimal two-column table configuration."""
        return m.Cli.TableConfig(headers=("Key", "Value"))

    def test_normalize_mapping_input_yields_key_value_rows(self) -> None:
        result = u.Cli.tables_normalize_data({"alpha": 1, "beta": 2})

        tm.ok(result)
        tm.that(
            result.unwrap(),
            eq=[{"Key": "alpha", "Value": 1}, {"Key": "beta", "Value": 2}],
        )

    def test_normalize_sequence_of_mapping_rows_preserves_row_shape(self) -> None:
        result = u.Cli.tables_normalize_data([{"Key": "a", "Value": 1}])

        tm.ok(result)
        tm.that(result.unwrap(), eq=[{"Key": "a", "Value": 1}])

    def test_normalize_sequence_of_sequence_rows_produces_lists(self) -> None:
        result = u.Cli.tables_normalize_data([["a", 1], ["b", 2]])

        tm.ok(result)
        tm.that(result.unwrap(), eq=[["a", 1], ["b", 2]])

    def test_normalize_empty_sequence_yields_empty_rows(self) -> None:
        result = u.Cli.tables_normalize_data([])

        tm.ok(result)
        tm.that(result.unwrap(), eq=[])

    @pytest.mark.parametrize("bad_data", [["abc"], ["x", "y"], [["ok", 1], "bad-row"]])
    def test_normalize_rejects_string_rows_as_data_invalid(
        self, bad_data: t.Cli.TableDataSource
    ) -> None:
        result = u.Cli.tables_normalize_data(bad_data)

        tm.fail(result)
        tm.that((result.error or ""), has=c.Cli.OUTPUT_TABLE_DATA_INVALID)

    def test_render_returns_string_containing_cell_values(
        self, two_column_config: m.Cli.TableConfig
    ) -> None:
        result = u.Cli.tables_render([{"Key": "a", "Value": 1}], two_column_config)

        tm.ok(result)
        rendered = result.unwrap()
        tm.that(rendered, is_=str)
        tm.that(rendered, has="Key")
        tm.that(rendered, has="a")

    def test_render_trims_overlong_colalign_to_column_count(self) -> None:
        settings = m.Cli.TableConfig(
            headers=("Key", "Value"), colalign=("left", "right", "center")
        )

        result = u.Cli.tables_render([{"Key": "a", "Value": 1}], settings)

        tm.ok(result)
        tm.that(result.unwrap(), is_=str)

    def test_render_without_header_omits_header_labels(self) -> None:
        result = u.Cli.tables_render(
            [["a", 1]], m.Cli.TableConfig(show_header=False, headers=("col1", "col2"))
        )

        tm.ok(result)
        rendered = result.unwrap()
        tm.that(rendered, lacks="col1")
        tm.that(rendered, has="a")

    def test_render_empty_rows_still_succeeds(
        self, two_column_config: m.Cli.TableConfig
    ) -> None:
        result = u.Cli.tables_render([], two_column_config)

        tm.ok(result)
        tm.that(result.unwrap(), is_=str)

    def test_render_is_idempotent_for_same_input(
        self, two_column_config: m.Cli.TableConfig
    ) -> None:
        rows: t.SequenceOf[t.Cli.TableRow] = [{"Key": "a", "Value": 1}]

        first = u.Cli.tables_render(rows, two_column_config)
        second = u.Cli.tables_render(rows, two_column_config)

        tm.ok(first)
        tm.ok(second)
        tm.that(first.unwrap(), eq=second.unwrap())

    def test_resolve_config_returns_provided_settings_unchanged(
        self, two_column_config: m.Cli.TableConfig
    ) -> None:
        result = u.Cli.tables_resolve_config(two_column_config)

        tm.ok(result)
        tm.that(result.unwrap().headers, eq=("Key", "Value"))

    def test_resolve_config_reports_invalid_override_as_failure(
        self, two_column_config: m.Cli.TableConfig
    ) -> None:
        result = u.Cli.tables_resolve_config(two_column_config, show_header="nope")

        tm.fail(result)
        tm.that((result.error or ""), has=c.Cli.OUTPUT_TABLE_CONFIG_INVALID)

    def test_normalize_then_render_round_trips_mapping_source(
        self, two_column_config: m.Cli.TableConfig
    ) -> None:
        normalized = u.Cli.tables_normalize_data({"alpha": 1})
        tm.ok(normalized)

        rendered = u.Cli.tables_render(normalized.unwrap(), two_column_config)

        tm.ok(rendered)
        tm.that(rendered.unwrap(), has="alpha")


__all__: list[str] = ["TestsFlextCliTablesBranchCov"]
