"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

import pytest

from flext_tests import tm
from tests import c, u


class TestsFlextCliOutputCov:
    """Implementation part for TestsFlextCliOutputCov."""

    def test_output_resolve_message_type_with_none(self) -> None:
        """Verify that output resolve message type with none."""
        result = u.Cli.output_resolve_message_type(None)
        tm.that(result, eq=c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE)

    def test_output_resolve_message_type_with_value(self) -> None:
        """Verify that output resolve message type with value."""
        result = u.Cli.output_resolve_message_type(c.Cli.MessageTypes.SUCCESS)
        tm.that(result, eq=c.Cli.MessageTypes.SUCCESS)

    def test_output_resolve_style_with_none(self) -> None:
        """Verify that output resolve style with none."""
        result = u.Cli.output_resolve_style(None)
        tm.that(result, eq=c.Cli.OUTPUT_EMPTY_STYLE)

    def test_output_resolve_style_with_value(self) -> None:
        """Verify that output resolve style with value."""
        result = u.Cli.output_resolve_style("bold red")
        tm.that(result, eq="bold red")

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
        """Verify that output message payload types."""
        text, style = u.Cli.output_message_payload("test message", msg_type)
        tm.that(text, has="test message")
        tm.that(style, is_=str)

    def test_output_progress_line_with_detail(self) -> None:
        """Verify that output progress line with detail."""
        line = u.Cli.output_progress_line(3, 10, "project-x", detail="building")
        tm.that(line, has="3")
        tm.that(line, has="10")
        tm.that(line, has="project-x")
        tm.that(line, has="building")

    def test_output_progress_line_no_detail(self) -> None:
        """Verify that output progress line no detail."""
        line = u.Cli.output_progress_line(1, 5, "label", detail="")
        tm.that(line, has="label")
        tm.that(line, lacks="building")

    def test_output_status_line_success(self) -> None:
        """Verify that output status line success."""
        line, style = u.Cli.output_status_line(
            "build", "flext-cli", success=True, elapsed=1.23
        )
        tm.that(line, is_=str)
        tm.that(style, is_=str)
        tm.that(line, has="1.23")

    def test_output_status_line_failure_no_elapsed(self) -> None:
        """Verify that output status line failure no elapsed."""
        line, _style = u.Cli.output_status_line(
            "test", "flext-core", success=False, elapsed=None
        )
        tm.that(line, is_=str)
        tm.that(line, lacks="s)")

    def test_output_gate_line_passed(self) -> None:
        """Verify that output gate line passed."""
        line, _style = u.Cli.output_gate_line("ruff", passed=True, message="clean")
        tm.that(line, has="ruff")
        tm.that(line, has="clean")

    def test_output_gate_line_failed_no_message(self) -> None:
        """Verify that output gate line failed no message."""
        line, _style = u.Cli.output_gate_line("mypy", passed=False, message="")
        tm.that(line, has="mypy")

    def test_output_summary_content(self) -> None:
        """Verify that output summary content."""
        result = u.Cli.output_summary_content(total=10, success=8, failed=1, skipped=1)
        tm.that(result, has="10")
        tm.that(result, has="8")
        tm.that(result, has="1")

    def test_output_debug_line(self) -> None:
        """Verify that output debug line."""
        line, _style = u.Cli.output_debug_line("hello debug")
        tm.that(line, has="hello debug")
        tm.that(line, has="DEBUG")

    def test_output_table_error_with_message(self) -> None:
        """Verify that output table error with message."""
        line, _style = u.Cli.output_table_error("col mismatch")
        tm.that(line, has="col mismatch")

    def test_output_table_error_none(self) -> None:
        """Verify that output table error none."""
        line, _style = u.Cli.output_table_error(None)
        tm.that(line, has=c.Cli.ERR_UNKNOWN_ERROR)

    def test_emit_raw(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that emit raw."""
        u.Cli.emit_raw("hello test\n")
        out = capsys.readouterr().out
        tm.that(out, has="hello test")

    def test_info(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that info."""
        u.Cli.info("test info")
        out = capsys.readouterr().out
        tm.that(out, has="test info")

    def test_error_with_detail(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that error with detail."""
        u.Cli.error("fail msg", detail="extra detail")
        out = capsys.readouterr().out
        tm.that(out, has="fail msg")
        tm.that(out, has="extra detail")

    def test_error_no_detail(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that error no detail."""
        u.Cli.error("just error")
        out = capsys.readouterr().out
        tm.that(out, has="just error")

    def test_warning(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that warning."""
        u.Cli.warning("be warned")
        out = capsys.readouterr().out
        tm.that(out, has="be warned")

    def test_debug(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that debug."""
        u.Cli.debug("debug message")
        out = capsys.readouterr().out
        tm.that(out, has="debug message")

    def test_header(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that header."""
        u.Cli.header("My Title")
        out = capsys.readouterr().out
        tm.that(out, has="My Title")

    def test_progress(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that progress."""
        u.Cli.progress(2, 5, "my-proj", "build")
        out = capsys.readouterr().out
        tm.that(out, has="my-proj")

    def test_status_ok(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that status ok."""
        u.Cli.status("build", "flext-cli", result=True, elapsed=0.5)
        out = capsys.readouterr().out
        tm.that(out, has="flext-cli")


__all__: list[str] = ["TestsFlextCliOutputCov"]
