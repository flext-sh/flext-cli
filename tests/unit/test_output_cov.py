"""Behavioral tests for ``u.Cli`` output helpers (public contract)."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm

from tests import c, u


class TestsFlextCliOutputCov:
    """Contract of the pure builders and stdout emitters exposed via ``u.Cli``."""

    # ---- pure resolvers -------------------------------------------------

    def test_resolve_message_type_none_falls_back_to_default(self) -> None:
        """Verify that resolve message type none falls back to default."""
        tm.that(
            u.Cli.output_resolve_message_type(None)
            == c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE,
            eq=True,
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
        self, msg_type: c.Cli.MessageTypes
    ) -> None:
        """Verify that resolve message type preserves explicit value."""
        tm.that(u.Cli.output_resolve_message_type(msg_type), eq=msg_type)

    def test_resolve_style_none_yields_empty_style(self) -> None:
        """Verify that resolve style none yields empty style."""
        tm.that(u.Cli.output_resolve_style(None), eq=c.Cli.OUTPUT_EMPTY_STYLE)

    def test_resolve_style_preserves_explicit_value(self) -> None:
        """Verify that resolve style preserves explicit value."""
        tm.that(u.Cli.output_resolve_style("bold red"), eq="bold red")

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
        self, msg_type: c.Cli.MessageTypes | None
    ) -> None:
        """Verify that message payload carries message and canonical style."""
        text, style = u.Cli.output_message_payload("hello", msg_type)
        resolved = u.Cli.output_resolve_message_type(msg_type)
        expected_style = c.Cli.MESSAGE_STYLE_MAP[resolved]
        expected_emoji = c.Cli.MESSAGE_EMOJI_MAP[resolved]
        tm.that(text, eq=f"{expected_emoji} hello")
        tm.that(style, eq=expected_style)

    # ---- progress line --------------------------------------------------

    def test_progress_line_zero_pads_and_appends_detail(self) -> None:
        """Verify that progress line zero pads and appends detail."""
        line = u.Cli.output_progress_line(3, 10, "project-x", detail="building")
        tm.that(line, eq="[03/10] project-x building")

    def test_progress_line_omits_detail_when_empty(self) -> None:
        """Verify that progress line omits detail when empty."""
        line = u.Cli.output_progress_line(1, 5, "label", detail="")
        tm.that(line, eq="[1/5] label")

    # ---- status line ----------------------------------------------------

    def test_status_line_success_includes_timing_and_green_style(self) -> None:
        """Verify that status line success includes timing and green style."""
        line, style = u.Cli.output_status_line(True, "build", "flext-cli", elapsed=1.23)
        tm.that(line, has="(1.23s)")
        tm.that(line, has=c.Cli.SYMBOL_SUCCESS_MARK)
        tm.that(style, eq=c.Cli.MessageStyles.BOLD_GREEN)

    def test_status_line_failure_without_elapsed_omits_timing(self) -> None:
        """Verify that status line failure without elapsed omits timing."""
        line, style = u.Cli.output_status_line(
            False, "test", "flext-core", elapsed=None
        )
        tm.that(line, lacks="s)")
        tm.that(line, has=c.Cli.SYMBOL_FAILURE_MARK)
        tm.that(style, eq=c.Cli.MessageStyles.BOLD_RED)

    # ---- gate line ------------------------------------------------------

    def test_gate_line_passed_shows_name_message_and_green_style(self) -> None:
        """Verify that gate line passed shows name message and green style."""
        line, style = u.Cli.output_gate_line("ruff", True, message="clean")
        tm.that(line, has="ruff")
        tm.that(line, has="clean")
        tm.that(style, eq=c.Cli.MessageStyles.BOLD_GREEN)

    def test_gate_line_failed_without_message_shows_name_and_red_style(self) -> None:
        """Verify that gate line failed without message shows name and red style."""
        line, style = u.Cli.output_gate_line("mypy", False, message="")
        tm.that(line, has="mypy")
        tm.that(style, eq=c.Cli.MessageStyles.BOLD_RED)

    # ---- summary / debug / table error ---------------------------------

    def test_summary_content_reports_all_counts(self) -> None:
        """Verify that summary content reports all counts."""
        content = u.Cli.output_summary_content(total=10, success=8, failed=1, skipped=0)
        tm.that(content, eq="Total: 10  Success: 8  Failed: 1  Skipped: 0")

    def test_debug_line_labels_message_and_uses_dim_style(self) -> None:
        """Verify that debug line labels message and uses dim style."""
        line, style = u.Cli.output_debug_line("hello debug")
        tm.that(line, has="hello debug")
        tm.that(line, has=c.Cli.OUTPUT_LOG_LEVEL_DEBUG)
        tm.that(style, eq=c.Cli.MessageStyles.DIM)

    def test_table_error_uses_given_message_with_red_style(self) -> None:
        """Verify that table error uses given message with red style."""
        line, style = u.Cli.output_table_error("col mismatch")
        tm.that(line, has="col mismatch")
        tm.that(style, eq=c.Cli.MessageStyles.BOLD_RED)

    def test_table_error_falls_back_to_unknown_error(self) -> None:
        """Verify that table error falls back to unknown error."""
        line, _style = u.Cli.output_table_error(None)
        tm.that(line, has=c.Cli.ERR_UNKNOWN_ERROR)

    # ---- stdout emitters ------------------------------------------------

    def test_emit_raw_writes_text_verbatim(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that emit raw writes text verbatim."""
        u.Cli.emit_raw("hello test\n")
        tm.that(capsys.readouterr().out, eq="hello test\n")

    def test_info_emits_message_with_info_level(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that info emits message with info level."""
        u.Cli.info("test info")
        out = capsys.readouterr().out
        tm.that(out, has="test info")
        tm.that(out, has=c.Cli.OUTPUT_LOG_LEVEL_INFO)

    def test_error_with_detail_emits_both_lines(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that error with detail emits both lines."""
        u.Cli.error("fail msg", detail="extra detail")
        out = capsys.readouterr().out
        tm.that(out, has="fail msg")
        tm.that(out, has="extra detail")

    def test_error_without_detail_omits_detail_indent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that error without detail omits detail indent."""
        u.Cli.error("just error")
        out = capsys.readouterr().out
        tm.that(out, has="just error")
        tm.that(out.endswith("  \n"), eq=False)

    def test_warning_emits_message_with_warning_level(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that warning emits message with warning level."""
        u.Cli.warning("be warned")
        out = capsys.readouterr().out
        tm.that(out, has="be warned")
        tm.that(out, has=c.Cli.OUTPUT_LOG_LEVEL_WARNING)

    def test_debug_emits_message_with_debug_level(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that debug emits message with debug level."""
        u.Cli.debug("debug message")
        out = capsys.readouterr().out
        tm.that(out, has="debug message")
        tm.that(out, has=c.Cli.OUTPUT_LOG_LEVEL_DEBUG)

    def test_header_frames_title_with_rules(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that header frames title with rules."""
        u.Cli.header("My Title")
        out = capsys.readouterr().out
        tm.that(out, has="My Title")
        tm.that(out, has="=" * c.Cli.OUTPUT_HEADER_RULE_WIDTH)

    def test_progress_emits_project_and_verb(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that progress emits project and verb."""
        u.Cli.progress(2, 5, "my-proj", "build")
        out = capsys.readouterr().out
        tm.that(out, has="my-proj")
        tm.that(out, has="build")

    @pytest.mark.parametrize(
        ("result", "symbol"),
        [(True, c.Cli.OUTPUT_STATUS_OK), (False, c.Cli.OUTPUT_STATUS_FAIL)],
    )
    def test_status_emits_project_and_result_symbol(
        self, capsys: pytest.CaptureFixture[str], *, result: bool, symbol: str
    ) -> None:
        """Verify that status emits project and result symbol."""
        u.Cli.status("build", "flext-cli", result=result, elapsed=0.5)
        out = capsys.readouterr().out
        tm.that(out, has="flext-cli")
        tm.that(out, has=symbol)

    def test_gate_result_emits_gate_name(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that gate result emits gate name."""
        u.Cli.gate_result("ruff", 0, passed=True, elapsed=0.2)
        out = capsys.readouterr().out
        tm.that(out, has="ruff")
        tm.that(out, has=c.Cli.OUTPUT_STATUS_OK)

    def test_summary_emits_verb_and_counts(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that summary emits verb and counts."""

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
        tm.that(out, has="Total: 5")

    def test_project_failure_lists_errors_and_truncation_notice(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that project failure lists errors and truncation notice."""

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
        # max_show=1 with error_count=2 -> one line shown, remainder summarized.
        tm.that(out, lacks="error line 2")
        tm.that(out, has="1 more")

    # ---- report path resolution ----------------------------------------

    def test_resolve_report_dir_workspace_scope_includes_scope_and_verb(
        self, tmp_path: Path
    ) -> None:
        """Verify that resolve report dir workspace scope includes scope and verb."""
        result = u.Cli.resolve_report_dir(
            tmp_path, c.Cli.OUTPUT_SCOPE_WORKSPACE, "check"
        )
        tm.that(result.parent.name, eq=c.Cli.OUTPUT_SCOPE_WORKSPACE)
        tm.that(result.name, eq="check")

    def test_resolve_report_dir_project_scope_ends_with_verb(
        self, tmp_path: Path
    ) -> None:
        """Verify that resolve report dir project scope ends with verb."""
        result = u.Cli.resolve_report_dir(tmp_path, "project", "test")
        tm.that(result.name, eq="test")
        tm.that(result.parent.name, eq=c.Cli.OUTPUT_REPORTS_DIR_NAME)

    def test_resolve_report_path_appends_filename(self, tmp_path: Path) -> None:
        """Verify that resolve report path appends filename."""
        result = u.Cli.resolve_report_path(
            str(tmp_path), c.Cli.OUTPUT_SCOPE_WORKSPACE, "check", "report.json"
        )
        tm.that(result.name, eq="report.json")
        tm.that(
            result.parent,
            eq=u.Cli.resolve_report_dir(
                tmp_path, c.Cli.OUTPUT_SCOPE_WORKSPACE, "check"
            ),
        )


__all__: list[str] = ["TestsFlextCliOutputCov"]
