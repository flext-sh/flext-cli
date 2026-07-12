"""Behavioral contract tests for the ``u.Cli.tables_*`` public surface."""

from __future__ import annotations

import pytest

from tests.constants import c
from tests.models import m
from tests.typings import t
from tests.utilities import u


class TestsFlextCliTablesBranchCov:
    """Assert the observable contract of the ``u.Cli`` table helpers."""

    @pytest.fixture
    def two_column_config(self) -> m.Cli.TableConfig:
        """Return a minimal two-column table configuration."""
        return m.Cli.TableConfig(headers=("Key", "Value"))

    def test_normalize_mapping_input_yields_key_value_rows(self) -> None:
        result = u.Cli.tables_normalize_data({"alpha": 1, "beta": 2})

        assert result.success
        assert result.unwrap() == [
            {"Key": "alpha", "Value": 1},
            {"Key": "beta", "Value": 2},
        ]

    def test_normalize_sequence_of_mapping_rows_preserves_row_shape(self) -> None:
        result = u.Cli.tables_normalize_data([{"Key": "a", "Value": 1}])

        assert result.success
        assert result.unwrap() == [{"Key": "a", "Value": 1}]

    def test_normalize_sequence_of_sequence_rows_produces_lists(self) -> None:
        result = u.Cli.tables_normalize_data([["a", 1], ["b", 2]])

        assert result.success
        assert result.unwrap() == [["a", 1], ["b", 2]]

    def test_normalize_empty_sequence_yields_empty_rows(self) -> None:
        result = u.Cli.tables_normalize_data([])

        assert result.success
        assert result.unwrap() == []

    @pytest.mark.parametrize(
        "bad_data",
        [
            ["abc"],
            ["x", "y"],
            [["ok", 1], "bad-row"],
        ],
    )
    def test_normalize_rejects_string_rows_as_data_invalid(
        self,
        bad_data: t.Cli.TableDataSource,
    ) -> None:
        result = u.Cli.tables_normalize_data(bad_data)

        assert result.failure
        assert c.Cli.OUTPUT_TABLE_DATA_INVALID in (result.error or "")

    def test_render_returns_string_containing_cell_values(
        self,
        two_column_config: m.Cli.TableConfig,
    ) -> None:
        result = u.Cli.tables_render([{"Key": "a", "Value": 1}], two_column_config)

        assert result.success
        rendered = result.unwrap()
        assert isinstance(rendered, str)
        assert "Key" in rendered
        assert "a" in rendered

    def test_render_trims_overlong_colalign_to_column_count(self) -> None:
        settings = m.Cli.TableConfig(
            headers=("Key", "Value"),
            colalign=("left", "right", "center"),
        )

        result = u.Cli.tables_render([{"Key": "a", "Value": 1}], settings)

        assert result.success
        assert isinstance(result.unwrap(), str)

    def test_render_without_header_omits_header_labels(self) -> None:
        result = u.Cli.tables_render(
            [["a", 1]],
            m.Cli.TableConfig(show_header=False, headers=("col1", "col2")),
        )

        assert result.success
        rendered = result.unwrap()
        assert "col1" not in rendered
        assert "a" in rendered

    def test_render_empty_rows_still_succeeds(
        self,
        two_column_config: m.Cli.TableConfig,
    ) -> None:
        result = u.Cli.tables_render([], two_column_config)

        assert result.success
        assert isinstance(result.unwrap(), str)

    def test_render_is_idempotent_for_same_input(
        self,
        two_column_config: m.Cli.TableConfig,
    ) -> None:
        rows: t.SequenceOf[t.Cli.TableRow] = [{"Key": "a", "Value": 1}]

        first = u.Cli.tables_render(rows, two_column_config)
        second = u.Cli.tables_render(rows, two_column_config)

        assert first.success
        assert second.success
        assert first.unwrap() == second.unwrap()

    def test_resolve_config_returns_provided_settings_unchanged(
        self,
        two_column_config: m.Cli.TableConfig,
    ) -> None:
        result = u.Cli.tables_resolve_config(two_column_config)

        assert result.success
        assert result.unwrap().headers == ("Key", "Value")

    def test_resolve_config_reports_invalid_override_as_failure(
        self,
        two_column_config: m.Cli.TableConfig,
    ) -> None:
        result = u.Cli.tables_resolve_config(two_column_config, show_header="nope")

        assert result.failure
        assert c.Cli.OUTPUT_TABLE_CONFIG_INVALID in (result.error or "")

    def test_normalize_then_render_round_trips_mapping_source(
        self,
        two_column_config: m.Cli.TableConfig,
    ) -> None:
        normalized = u.Cli.tables_normalize_data({"alpha": 1})
        assert normalized.success

        rendered = u.Cli.tables_render(normalized.unwrap(), two_column_config)

        assert rendered.success
        assert "alpha" in rendered.unwrap()


__all__: list[str] = ["TestsFlextCliTablesBranchCov"]
