"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

import pytest
from tests.constants import c
from tests.utilities import u


class TestsFlextCliOutputCov:
    """Implementation part for TestsFlextCliOutputCov."""

    def test_output_resolve_message_type_with_none(self) -> None:
        result = u.Cli.output_resolve_message_type(None)
        assert result == c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE

    def test_output_resolve_message_type_with_value(self) -> None:
        result = u.Cli.output_resolve_message_type(c.Cli.MessageTypes.SUCCESS)
        assert result == c.Cli.MessageTypes.SUCCESS

    def test_output_resolve_style_with_none(self) -> None:
        result = u.Cli.output_resolve_style(None)
        assert result == c.Cli.OUTPUT_EMPTY_STYLE

    def test_output_resolve_style_with_value(self) -> None:
        result = u.Cli.output_resolve_style("bold red")
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
        self,
        msg_type: c.Cli.MessageTypes | None,
    ) -> None:
        text, style = u.Cli.output_message_payload("test message", msg_type)
        assert "test message" in text
        assert isinstance(style, str)

    def test_output_progress_line_with_detail(self) -> None:
        line = u.Cli.output_progress_line(3, 10, "project-x", detail="building")
        assert "3" in line
        assert "10" in line
        assert "project-x" in line
        assert "building" in line

    def test_output_progress_line_no_detail(self) -> None:
        line = u.Cli.output_progress_line(1, 5, "label", detail="")
        assert "label" in line
        assert "building" not in line

    def test_output_status_line_success(self) -> None:
        line, style = u.Cli.output_status_line(True, "build", "flext-cli", elapsed=1.23)
        assert isinstance(line, str)
        assert isinstance(style, str)
        assert "1.23" in line

    def test_output_status_line_failure_no_elapsed(self) -> None:
        line, _style = u.Cli.output_status_line(
            False,
            "test",
            "flext-core",
            elapsed=None,
        )
        assert isinstance(line, str)
        assert "s)" not in line

    def test_output_gate_line_passed(self) -> None:
        line, _style = u.Cli.output_gate_line("ruff", True, message="clean")
        assert "ruff" in line
        assert "clean" in line

    def test_output_gate_line_failed_no_message(self) -> None:
        line, _style = u.Cli.output_gate_line("mypy", False, message="")
        assert "mypy" in line

    def test_output_summary_content(self) -> None:
        result = u.Cli.output_summary_content(total=10, success=8, failed=1, skipped=1)
        assert "10" in result
        assert "8" in result
        assert "1" in result

    def test_output_debug_line(self) -> None:
        line, _style = u.Cli.output_debug_line("hello debug")
        assert "hello debug" in line
        assert "DEBUG" in line

    def test_output_table_error_with_message(self) -> None:
        line, _style = u.Cli.output_table_error("col mismatch")
        assert "col mismatch" in line

    def test_output_table_error_none(self) -> None:
        line, _style = u.Cli.output_table_error(None)
        assert c.Cli.ERR_UNKNOWN_ERROR in line

    def test_emit_raw(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.emit_raw("hello test\n")
        out = capsys.readouterr().out
        assert "hello test" in out

    def test_info(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.info("test info")
        out = capsys.readouterr().out
        assert "test info" in out

    def test_error_with_detail(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.error("fail msg", detail="extra detail")
        out = capsys.readouterr().out
        assert "fail msg" in out
        assert "extra detail" in out

    def test_error_no_detail(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.error("just error")
        out = capsys.readouterr().out
        assert "just error" in out

    def test_warning(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.warning("be warned")
        out = capsys.readouterr().out
        assert "be warned" in out

    def test_debug(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.debug("debug message")
        out = capsys.readouterr().out
        assert "debug message" in out

    def test_header(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.header("My Title")
        out = capsys.readouterr().out
        assert "My Title" in out

    def test_progress(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.progress(2, 5, "my-proj", "build")
        out = capsys.readouterr().out
        assert "my-proj" in out

    def test_status_ok(self, capsys: pytest.CaptureFixture[str]) -> None:
        u.Cli.status("build", "flext-cli", result=True, elapsed=0.5)
        out = capsys.readouterr().out
        assert "flext-cli" in out


__all__: list[str] = ["TestsFlextCliOutputCov"]
