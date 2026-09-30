"""Behavioral tests for the generic data report facade ``u.Cli.report_*``."""

from __future__ import annotations

from flext_cli import m, u


class TestsFlextCliDataReport:
    """Contract of the generic data report render/emit owner."""

    def test_report_render_renders_title_headers_and_rows(self) -> None:
        """The rendered table carries the column labels and row values."""
        request = m.Cli.DataReportRequest(
            columns=("bead", "action"),
            rows=[["aihub-1", "land"], ["aihub-2", "clean"]],
            title="wip next",
        )
        rendered = u.Cli.report_render(request)
        assert rendered.success
        assert "bead" in rendered.value
        assert "aihub-1" in rendered.value
        assert "clean" in rendered.value

    def test_report_render_accepts_an_empty_report(self) -> None:
        """An empty report renders deterministically without failing."""
        rendered = u.Cli.report_render(m.Cli.DataReportRequest(columns=(), rows=()))
        assert rendered.success

    def test_report_emit_json_returns_success(self) -> None:
        """Emitting the typed report as JSON returns the success boundary."""
        emitted = u.Cli.report_emit(
            m.Cli.DataReportRequest(columns=("a",), rows=[["b"]]), json_output=True
        )
        assert emitted.success

    def test_report_emit_table_returns_success(self) -> None:
        """Emitting the typed report as a table returns the success boundary."""
        emitted = u.Cli.report_emit(
            m.Cli.DataReportRequest(columns=("a",), rows=[["b"]], message="verdict"),
            json_output=False,
        )
        assert emitted.success
