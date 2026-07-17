"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

from pathlib import Path

from tests import c
from tests import u
from flext_tests import tm

import pytest


class TestsFlextCliOutputCov:
    """Implementation part for TestsFlextCliOutputCov."""

    def test_status_fail(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that status fail."""
        u.Cli.status("test", "flext-core", result=False, elapsed=1.1)
        out = capsys.readouterr().out
        tm.that(out, has="flext-core")

    def test_gate_result(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that gate result."""
        u.Cli.gate_result("ruff", 0, passed=True, elapsed=0.2)
        out = capsys.readouterr().out
        tm.that(out, has="ruff")

    def test_resolve_report_dir_workspace_scope(self, tmp_path: Path) -> None:
        """Verify that resolve report dir workspace scope."""
        result = u.Cli.resolve_report_dir(
            tmp_path, c.Cli.OUTPUT_SCOPE_WORKSPACE, "check"
        )
        tm.that(str(result), has=c.Cli.OUTPUT_SCOPE_WORKSPACE)
        tm.that(str(result), has="check")

    def test_resolve_report_dir_project_scope(self, tmp_path: Path) -> None:
        """Verify that resolve report dir project scope."""
        result = u.Cli.resolve_report_dir(tmp_path, "project", "test")
        tm.that(str(result), has="test")

    def test_resolve_report_path(self, tmp_path: Path) -> None:
        """Verify that resolve report path."""
        result = u.Cli.resolve_report_path(
            str(tmp_path), c.Cli.OUTPUT_SCOPE_WORKSPACE, "check", "report.json"
        )
        tm.that(result.name, eq="report.json")

    def test_summary(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that summary."""

        class _FakeSummaryStats:
            verb = "check"
            total = 5
            success = 4
            failed = 1
            skipped = 0
            elapsed = 2.5

        u.Cli.summary(_FakeSummaryStats())
        out = capsys.readouterr().out
        tm.that(out, has="check")

    def test_project_failure(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that project failure."""

        class _FakeProjectFailureInfo:
            project = "flext-cli"
            elapsed = 3.0
            error_count = 2
            log_path = Path("log.txt")
            max_show = 1
            errors = ("error line 1", "error line 2")

        u.Cli.project_failure(_FakeProjectFailureInfo())
        out = capsys.readouterr().out
        tm.that(out, has="flext-cli")
        tm.that(out, has="error line 1")
        # "and 1 more" should appear because max_show=1 but error_count=2
        tm.that(out, has="more")


__all__: list[str] = ["TestsFlextCliOutputCov"]
