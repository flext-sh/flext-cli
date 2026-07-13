"""Behavioral tests for ``u.Cli`` output helpers (public contract)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.constants import c
from tests.utilities import u


class TestsFlextCliOutputCov:
    """Contract of the pure builders and stdout emitters exposed via ``u.Cli``."""

    # ---- pure resolvers -------------------------------------------------

    def test_resolve_message_type_none_falls_back_to_default(self) -> None:
        assert (
            u.Cli.output_resolve_message_type(None) == c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE
        )

    @pytest.mark.parametrize(
        "msg_type",
        [
            c.Cli.MessageTypes.SUCCESS,
            c.Cli.MessageTypes.ERROR,
            c.Cli.MessageTypes.WARNING,
            c.Cli.MessageTypes.INFO,
        ],
    )
    def test_resolve_message_type_preserves_explicit_value(
        self,
        msg_type: c.Cli.MessageTypes,
    ) -> None:
        assert u.Cli.output_resolve_message_type(msg_type) == msg_type

    def test_resolve_style_none_yields_empty_style(self) -> None:
        assert u.Cli.output_resolve_style(None) == c.Cli.OUTPUT_EMPTY_STYLE

    def test_resolve_style_preserves_explicit_value(self) -> None:
        assert u.Cli.output_resolve_style("bold red") == "bold red"

    # ---- message payload ------------------------------------------------

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
    def test_message_payload_carries_message_and_canonical_style(
        self,
        msg_type: c.Cli.MessageTypes | None,
    ) -> None:
        text, style = u.Cli.output_message_payload("hello", msg_type)
        resolved = u.Cli.output_resolve_message_type(msg_type)
        expected_style = c.Cli.MESSAGE_STYLE_MAP[resolved]
        expected_emoji = c.Cli.MESSAGE_EMOJI_MAP[resolved]
        assert text == f"{expected_emoji} hello"
        assert style == expected_style

    # ---- progress line --------------------------------------------------

    def test_progress_line_zero_pads_and_appends_detail(self) -> None:
        line = u.Cli.output_progress_line(3, 10, "project-x", detail="building")
        assert line == "[03/10] project-x building"

    def test_progress_line_omits_detail_when_empty(self) -> None:
        line = u.Cli.output_progress_line(1, 5, "label", detail="")
        assert line == "[1/5] label"

    # ---- status line ----------------------------------------------------

    def test_status_line_success_includes_timing_and_green_style(self) -> None:
        line, style = u.Cli.output_status_line(
            True,
            "build",
            "flext-cli",
            elapsed=1.23,
        )
        assert "(1.23s)" in line
        assert c.Cli.SYMBOL_SUCCESS_MARK in line
        assert style == c.Cli.MessageStyles.BOLD_GREEN

    def test_status_line_failure_without_elapsed_omits_timing(self) -> None:
        line, style = u.Cli.output_status_line(
            False,
            "test",
            "flext-core",
            elapsed=None,
        )
        assert "s)" not in line
        assert c.Cli.SYMBOL_FAILURE_MARK in line
        assert style == c.Cli.MessageStyles.BOLD_RED

    # ---- gate line ------------------------------------------------------

    def test_gate_line_passed_shows_name_message_and_green_style(self) -> None:
        line, style = u.Cli.output_gate_line("ruff", True, message="clean")
        assert "ruff" in line
        assert "clean" in line
        assert style == c.Cli.MessageStyles.BOLD_GREEN

    def test_gate_line_failed_without_message_shows_name_and_red_style(self) -> None:
        line, style = u.Cli.output_gate_line("mypy", False, message="")
        assert "mypy" in line
        assert style == c.Cli.MessageStyles.BOLD_RED

    # ---- summary / debug / table error ---------------------------------

    def test_summary_content_reports_all_counts(self) -> None:
        content = u.Cli.output_summary_content(
            total=10,
            success=8,
            failed=1,
            skipped=0,
        )
        assert content == "Total: 10  Success: 8  Failed: 1  Skipped: 0"

    def test_debug_line_labels_message_and_uses_dim_style(self) -> None:
        line, style = u.Cli.output_debug_line("hello debug")
        assert "hello debug" in line
        assert c.Cli.OUTPUT_LOG_LEVEL_DEBUG in line
        assert style == c.Cli.MessageStyles.DIM

    def test_table_error_uses_given_message_with_red_style(self) -> None:
        line, style = u.Cli.output_table_error("col mismatch")
        assert "col mismatch" in line
        assert style == c.Cli.MessageStyles.BOLD_RED

    def test_table_error_falls_back_to_unknown_error(self) -> None:
        line, _style = u.Cli.output_table_error(None)
        assert c.Cli.ERR_UNKNOWN_ERROR in line

    # ---- stdout emitters ------------------------------------------------

    def test_emit_raw_writes_text_verbatim(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.emit_raw("hello test\n")
        assert capsys.readouterr().out == "hello test\n"

    def test_info_emits_message_with_info_level(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.info("test info")
        out = capsys.readouterr().out
        assert "test info" in out
        assert c.Cli.OUTPUT_LOG_LEVEL_INFO in out

    def test_error_with_detail_emits_both_lines(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.error("fail msg", detail="extra detail")
        out = capsys.readouterr().out
        assert "fail msg" in out
        assert "extra detail" in out

    def test_error_without_detail_omits_detail_indent(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.error("just error")
        out = capsys.readouterr().out
        assert "just error" in out
        assert "  \n" not in out

    def test_warning_emits_message_with_warning_level(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.warning("be warned")
        out = capsys.readouterr().out
        assert "be warned" in out
        assert c.Cli.OUTPUT_LOG_LEVEL_WARNING in out

    def test_debug_emits_message_with_debug_level(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.debug("debug message")
        out = capsys.readouterr().out
        assert "debug message" in out
        assert c.Cli.OUTPUT_LOG_LEVEL_DEBUG in out

    def test_header_frames_title_with_rules(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.header("My Title")
        out = capsys.readouterr().out
        assert "My Title" in out
        assert "=" * c.Cli.OUTPUT_HEADER_RULE_WIDTH in out

    def test_progress_emits_project_and_verb(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.progress(2, 5, "my-proj", "build")
        out = capsys.readouterr().out
        assert "my-proj" in out
        assert "build" in out

    @pytest.mark.parametrize(
        ("result", "symbol"),
        [
            (True, c.Cli.OUTPUT_STATUS_OK),
            (False, c.Cli.OUTPUT_STATUS_FAIL),
        ],
    )
    def test_status_emits_project_and_result_symbol(
        self,
        capsys: pytest.CaptureFixture[str],
        *,
        result: bool,
        symbol: str,
    ) -> None:
        u.Cli.status("build", "flext-cli", result=result, elapsed=0.5)
        out = capsys.readouterr().out
        assert "flext-cli" in out
        assert symbol in out

    def test_gate_result_emits_gate_name(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        u.Cli.gate_result("ruff", 0, passed=True, elapsed=0.2)
        out = capsys.readouterr().out
        assert "ruff" in out
        assert c.Cli.OUTPUT_STATUS_OK in out

    def test_summary_emits_verb_and_counts(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        class _FakeSummaryStats:
            verb = "check"
            total = 5
            success = 4
            failed = 1
            skipped = 0
            elapsed = 2.5

        u.Cli.summary(_FakeSummaryStats())
        out = capsys.readouterr().out
        assert "check" in out
        assert "Total: 5" in out

    def test_project_failure_lists_errors_and_truncation_notice(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        class _FakeProjectFailureInfo:
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
        # max_show=1 with error_count=2 -> one line shown, remainder summarized.
        assert "error line 2" not in out
        assert "1 more" in out

    # ---- report path resolution ----------------------------------------

    def test_resolve_report_dir_workspace_scope_includes_scope_and_verb(
        self,
        tmp_path: Path,
    ) -> None:
        result = u.Cli.resolve_report_dir(
            tmp_path,
            c.Cli.OUTPUT_SCOPE_WORKSPACE,
            "check",
        )
        assert result.parent.name == c.Cli.OUTPUT_SCOPE_WORKSPACE
        assert result.name == "check"

    def test_resolve_report_dir_project_scope_ends_with_verb(
        self,
        tmp_path: Path,
    ) -> None:
        result = u.Cli.resolve_report_dir(tmp_path, "project", "test")
        assert result.name == "test"
        assert result.parent.name == c.Cli.OUTPUT_REPORTS_DIR_NAME

    def test_resolve_report_path_appends_filename(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_report_path(
            str(tmp_path),
            c.Cli.OUTPUT_SCOPE_WORKSPACE,
            "check",
            "report.json",
        )
        assert result.name == "report.json"
        assert result.parent == u.Cli.resolve_report_dir(
            tmp_path,
            c.Cli.OUTPUT_SCOPE_WORKSPACE,
            "check",
        )


__all__: list[str] = ["TestsFlextCliOutputCov"]
