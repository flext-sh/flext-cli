"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

from pathlib import Path

import pytest

from flext_cli._utilities.output import FlextCliUtilitiesOutput
from tests import c, p


class TestsFlextCliOutputCov:
    """Coverage tests for output utility methods."""

    def test_output_resolve_message_type_with_none(self) -> None:
        result = FlextCliUtilitiesOutput.output_resolve_message_type(None)
        assert result == c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE

    def test_output_resolve_message_type_with_value(self) -> None:
        result = FlextCliUtilitiesOutput.output_resolve_message_type(
            c.Cli.MessageTypes.SUCCESS
        )
        assert result == c.Cli.MessageTypes.SUCCESS

    def test_output_resolve_style_with_none(self) -> None:
        result = FlextCliUtilitiesOutput.output_resolve_style(None)
        assert result == c.Cli.OUTPUT_EMPTY_STYLE

    def test_output_resolve_style_with_value(self) -> None:
        result = FlextCliUtilitiesOutput.output_resolve_style("bold red")
        assert result == "bold red"

    @pytest.mark.parametrize(
        "msg_type",
        [
            c.Cli.MessageTypes.SUCCESS,
            c.Cli.MessageTypes.ERROR,
            c.Cli.MessageTypes.WARNING,
            c.Cli.MessageTypes.INFO,
            None,
        ],
    )
    def test_output_message_payload_types(
        self, msg_type: c.Cli.MessageTypes | None
    ) -> None:
        text, style = FlextCliUtilitiesOutput.output_message_payload(
            "test message", msg_type
        )
        assert "test message" in text
        assert isinstance(style, str)

    def test_output_progress_line_with_detail(self) -> None:
        line = FlextCliUtilitiesOutput.output_progress_line(
            3, 10, "project-x", detail="building"
        )
        assert "3" in line
        assert "10" in line
        assert "project-x" in line
        assert "building" in line

    def test_output_progress_line_no_detail(self) -> None:
        line = FlextCliUtilitiesOutput.output_progress_line(1, 5, "label", detail="")
        assert "label" in line
        assert "building" not in line

    def test_output_status_line_success(self) -> None:
        line, style = FlextCliUtilitiesOutput.output_status_line(
            True, "build", "flext-cli", elapsed=1.23
        )
        assert isinstance(line, str)
        assert isinstance(style, str)
        assert "1.23" in line

    def test_output_status_line_failure_no_elapsed(self) -> None:
        line, _style = FlextCliUtilitiesOutput.output_status_line(
            False, "test", "flext-core", elapsed=None
        )
        assert isinstance(line, str)
        assert "s)" not in line

    def test_output_gate_line_passed(self) -> None:
        line, _style = FlextCliUtilitiesOutput.output_gate_line(
            "ruff", True, message="clean"
        )
        assert "ruff" in line
        assert "clean" in line

    def test_output_gate_line_failed_no_message(self) -> None:
        line, _style = FlextCliUtilitiesOutput.output_gate_line(
            "mypy", False, message=""
        )
        assert "mypy" in line

    def test_output_summary_content(self) -> None:
        result = FlextCliUtilitiesOutput.output_summary_content(
            total=10, success=8, failed=1, skipped=1
        )
        assert "10" in result
        assert "8" in result
        assert "1" in result

    def test_output_debug_line(self) -> None:
        line, _style = FlextCliUtilitiesOutput.output_debug_line("hello debug")
        assert "hello debug" in line
        assert "DEBUG" in line

    def test_output_table_error_with_message(self) -> None:
        line, _style = FlextCliUtilitiesOutput.output_table_error("col mismatch")
        assert "col mismatch" in line

    def test_output_table_error_none(self) -> None:
        line, _style = FlextCliUtilitiesOutput.output_table_error(None)
        assert "unknown error" in line

    def test_emit_raw(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.emit_raw("hello test\n")
        out = capsys.readouterr().out
        assert "hello test" in out

    def test_info(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.info("test info")
        out = capsys.readouterr().out
        assert "test info" in out

    def test_error_with_detail(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.error("fail msg", detail="extra detail")
        out = capsys.readouterr().out
        assert "fail msg" in out
        assert "extra detail" in out

    def test_error_no_detail(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.error("just error")
        out = capsys.readouterr().out
        assert "just error" in out

    def test_warning(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.warning("be warned")
        out = capsys.readouterr().out
        assert "be warned" in out

    def test_debug(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.debug("debug message")
        out = capsys.readouterr().out
        assert "debug message" in out

    def test_header(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.header("My Title")
        out = capsys.readouterr().out
        assert "My Title" in out

    def test_progress(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.progress(2, 5, "my-proj", "build")
        out = capsys.readouterr().out
        assert "my-proj" in out

    def test_status_ok(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.status("build", "flext-cli", result=True, elapsed=0.5)
        out = capsys.readouterr().out
        assert "flext-cli" in out

    def test_status_fail(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.status("test", "flext-core", result=False, elapsed=1.1)
        out = capsys.readouterr().out
        assert "flext-core" in out

    def test_gate_result(self, capsys: pytest.CaptureFixture[str]) -> None:
        FlextCliUtilitiesOutput.gate_result("ruff", 0, passed=True, elapsed=0.2)
        out = capsys.readouterr().out
        assert "ruff" in out

    def test_resolve_report_dir_workspace_scope(self, tmp_path: Path) -> None:
        result = FlextCliUtilitiesOutput.resolve_report_dir(
            tmp_path, "workspace", "check"
        )
        assert "workspace" in str(result)
        assert "check" in str(result)

    def test_resolve_report_dir_project_scope(self, tmp_path: Path) -> None:
        result = FlextCliUtilitiesOutput.resolve_report_dir(tmp_path, "project", "test")
        assert "test" in str(result)

    def test_resolve_report_path(self, tmp_path: Path) -> None:
        result = FlextCliUtilitiesOutput.resolve_report_path(
            str(tmp_path), "workspace", "check", "report.json"
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

        FlextCliUtilitiesOutput.summary(_FakeSummaryStats())
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

        FlextCliUtilitiesOutput.project_failure(_FakeProjectFailureInfo())
        out = capsys.readouterr().out
        assert "flext-cli" in out
        assert "error line 1" in out
        # "and 1 more" should appear because max_show=1 but error_count=2
        assert "more" in out
