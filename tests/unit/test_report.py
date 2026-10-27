"""Behavioral tests for the generic data report facade ``u.Cli.report_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import m, tm, u


class TestsFlextCliDataReport:
    """Contract of the generic data report render/emit owner."""

    @staticmethod
    def test_report_render_renders_title_headers_and_rows() -> None:
        """The rendered table carries the column labels and row values."""
        request = m.Cli.DataReportRequest(
            columns=("bead", "action"),
            rows=[["aihub-1", "land"], ["aihub-2", "clean"]],
            title="wip next",
        )
        rendered = u.Cli.report_render(request)
        tm.that(rendered.success, truth=True)
        tm.that("bead" in rendered.value, truth=True)
        tm.that("aihub-1" in rendered.value, truth=True)
        tm.that("clean" in rendered.value, truth=True)

    @staticmethod
    def test_report_render_accepts_an_empty_report() -> None:
        """An empty report renders deterministically without failing."""
        rendered = u.Cli.report_render(m.Cli.DataReportRequest(columns=(), rows=()))
        tm.that(rendered.success, truth=True)
