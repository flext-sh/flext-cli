"""Branch coverage tests for flext_cli.services.tables."""

from __future__ import annotations

import pytest

from flext_cli.services.tables import FlextCliTables


class TestsFlextCliServicesTablesBranchCov:
    """Exercise failure and title branches for FlextCliTables with real inputs."""

    def test_format_table_config_failure(self) -> None:
        result = FlextCliTables.format_table({"a": 1}, table_format="invalid")
        assert result.failure
        assert "Invalid table configuration" in (result.error or "")

    def test_show_table_config_failure_emits_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        FlextCliTables.show_table({"a": 1}, table_format="invalid")
        captured = capsys.readouterr()
        assert "Invalid table configuration" in captured.out

    def test_show_table_success_with_title_prints_title_and_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        FlextCliTables.show_table({"a": 1}, title="My Title")
        captured = capsys.readouterr()
        assert "My Title" in captured.out
        assert "a" in captured.out
        assert "1" in captured.out

    def test_show_table_list_payload_prints_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        FlextCliTables.show_table([["col1", "col2"], ["a", "b"]])
        captured = capsys.readouterr()
        assert "col1" in captured.out
        assert "a" in captured.out


__all__: list[str] = ["TestsFlextCliServicesTablesBranchCov"]
