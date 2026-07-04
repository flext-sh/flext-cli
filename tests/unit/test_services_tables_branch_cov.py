"""Branch coverage tests for flext_cli.services.tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from tests.constants import c

if TYPE_CHECKING:
    import pytest


class TestsFlextCliServicesTablesBranchCov:
    """Exercise failure and title branches for FlextCliTables with real inputs."""

    def test_format_table_config_failure(self) -> None:
        result = cli.format_table({"a": 1}, table_format="invalid")
        assert result.failure
        assert c.Cli.OUTPUT_TABLE_CONFIG_INVALID in (result.error or "")

    def test_show_table_config_failure_emits_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table({"a": 1}, table_format="invalid")
        captured = capsys.readouterr()
        assert c.Cli.OUTPUT_TABLE_CONFIG_INVALID in captured.out

    def test_show_table_success_with_title_prints_title_and_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table({"a": 1}, title="My Title")
        captured = capsys.readouterr()
        assert "My Title" in captured.out
        assert "a" in captured.out
        assert "1" in captured.out

    def test_show_table_list_payload_prints_table(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        cli.show_table([["col1", "col2"], ["a", "b"]])
        captured = capsys.readouterr()
        assert "col1" in captured.out
        assert "a" in captured.out


__all__: list[str] = ["TestsFlextCliServicesTablesBranchCov"]
