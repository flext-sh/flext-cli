"""Coverage tests for services/output.py.

Targets: display_message, display_text, print_message, display_header,
         display_progress, display_status, display_summary, display_gate,
         display_metrics, display_debug.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.services.output import FlextCliOutput
from tests import c


class TestsFlextCliServicesOutputCov:
    """Data-driven coverage tests for FlextCliOutput service."""

    # ── display_message ───────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("message", "message_type"),
        c.Tests.OUTPUT_DISPLAY_CASES,
    )
    def test_display_message_parametrized(
        self,
        message: str,
        message_type: c.Cli.MessageTypes | None,
    ) -> None:
        FlextCliOutput.display_message(message, message_type)

    # ── display_text ──────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("text", "style"),
        c.Tests.OUTPUT_TEXT_CASES,
    )
    def test_display_text_parametrized(self, text: str, style: str | None) -> None:
        if style is not None:
            FlextCliOutput.display_text(text, style=style)
        else:
            FlextCliOutput.display_text(text)

    # ── print_message ─────────────────────────────────────────────────

    def test_print_message_no_style(self) -> None:
        FlextCliOutput.print_message("no style message")

    def test_print_message_with_style(self) -> None:
        FlextCliOutput.print_message("styled message", "bold red")

    # ── display_header ────────────────────────────────────────────────

    @pytest.mark.parametrize("label", c.Tests.OUTPUT_HEADER_LABELS)
    def test_display_header_parametrized(self, label: str) -> None:
        FlextCliOutput.display_header(label)

    # ── display_progress ──────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("current", "total"),
        c.Tests.OUTPUT_PROGRESS_CASES,
    )
    def test_display_progress_parametrized(self, current: int, total: int) -> None:
        FlextCliOutput.display_progress(current, total, "Processing")

    def test_display_progress_with_detail(self) -> None:
        FlextCliOutput.display_progress(3, 10, "Steps", detail="step 3")

    # ── display_status ────────────────────────────────────────────────

    def test_display_status_passed(self) -> None:
        FlextCliOutput.display_status(True, "lint", "all clean")

    def test_display_status_failed(self) -> None:
        FlextCliOutput.display_status(False, "test", "3 failures")

    def test_display_status_with_elapsed(self) -> None:
        FlextCliOutput.display_status(True, "build", "ok", elapsed=1.23)

    # ── display_summary ───────────────────────────────────────────────

    def test_display_summary(self) -> None:
        FlextCliOutput.display_summary(
            "Run Summary",
            total=10,
            success=8,
            failed=2,
        )

    def test_display_summary_with_skipped(self) -> None:
        FlextCliOutput.display_summary(
            "Summary",
            total=10,
            success=7,
            failed=1,
            skipped=2,
        )

    # ── display_gate ──────────────────────────────────────────────────

    def test_display_gate_passed(self) -> None:
        FlextCliOutput.display_gate("ruff", True)

    def test_display_gate_failed(self) -> None:
        FlextCliOutput.display_gate("pyrefly", False, message="2 errors")

    # ── display_metrics ───────────────────────────────────────────────

    def test_display_metrics(self) -> None:
        FlextCliOutput.display_metrics({"total": 100, "passed": 95, "failed": 5})

    def test_display_metrics_empty(self) -> None:
        FlextCliOutput.display_metrics({})

    # ── display_debug ─────────────────────────────────────────────────

    def test_display_debug_no_verbose(self) -> None:
        # verbose=False → no output, no error
        FlextCliOutput.display_debug("debug msg", verbose=False)

    def test_display_debug_verbose(self) -> None:
        FlextCliOutput.display_debug("debug msg", verbose=True)


__all__: list[str] = ["TestsFlextCliServicesOutputCov"]
