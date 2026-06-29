"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.constants import c
from tests.utilities import u

from flext_cli import p


class TestsFlextCliOutputCov:
    """Implementation part for TestsFlextCliOutputCov."""

    def test_status_fail(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.status("test", "flext-core", result=False, elapsed=1.1)
        out = capsys.readouterr().out
        assert "flext-core" in out

    def test_gate_result(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.gate_result("ruff", 0, passed=True, elapsed=0.2)
        out = capsys.readouterr().out
        assert "ruff" in out

    def test_resolve_report_dir_workspace_scope(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_report_dir(
            tmp_path, c.Cli.OUTPUT_SCOPE_WORKSPACE, "check"
        )
        assert c.Cli.OUTPUT_SCOPE_WORKSPACE in str(result)
        assert "check" in str(result)

    def test_resolve_report_dir_project_scope(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_report_dir(tmp_path, "project", "test")
        assert "test" in str(result)

    def test_resolve_report_path(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_report_path(
            str(tmp_path), c.Cli.OUTPUT_SCOPE_WORKSPACE, "check", "report.json"
        )
        assert result.name == "report.json"

    def test_summary(self, capsys: pytest.CaptureFixture[str]) -> None:
        class _FakeSummaryStats(p.Cli.SummaryStats):
            verb = "check"
            total = 5
            success = 4
            failed = 1
            skipped = 0
            elapsed = 2.5

        u.Cli.summary(_FakeSummaryStats())
        out = capsys.readouterr().out
        assert "check" in out

    def test_project_failure(self, capsys: pytest.CaptureFixture[str]) -> None:
        class _FakeProjectFailureInfo(p.Cli.ProjectFailureInfo):
            project = "flext-cli"
            elapsed = 3.0
            error_count = 2
            log_path = Path("/tmp/log.txt")
            max_show = 1
            errors = ("error line 1", "error line 2")

        u.Cli.project_failure(_FakeProjectFailureInfo())
        out = capsys.readouterr().out
        assert "flext-cli" in out
        assert "error line 1" in out
        # "and 1 more" should appear because max_show=1 but error_count=2
        assert "more" in out


__all__: list[str] = ["TestsFlextCliOutputCov"]
