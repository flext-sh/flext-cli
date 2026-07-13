"""Behavioral tests for services/output.py (FlextCliOutput public API).

These tests assert the OBSERVABLE terminal output produced by the public
``FlextCliOutput`` display API (exposed via the ``cli`` facade). The captured
stdout is the real user-facing contract: the emoji/symbol, the formatted line
layout, the zero-padded progress counter, the panel content and the
no-op/idempotence invariants. No private attributes, collaborators or Rich
internals are inspected -- only what a user of the CLI actually sees.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import cli
from tests import c
from flext_tests import tm

type Capture = pytest.CaptureFixture[str]


class TestsFlextCliServicesOutputCov:
    """Observable-behavior tests for the FlextCliOutput display contract."""

    # ── display_message ───────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("message_type", "expected_marker"),
        [
            (c.Cli.MessageTypes.INFO, "i"),
            (c.Cli.MessageTypes.SUCCESS, "✅"),
            (c.Cli.MessageTypes.ERROR, "❌"),
            (c.Cli.MessageTypes.WARNING, "⚠"),
            (c.Cli.MessageTypes.DEBUG, "D"),
            (None, "i"),  # None resolves to the default INFO marker
        ],
    )
    def test_display_message_prefixes_type_marker_and_keeps_text(
        self,
        capsys: Capture,
        message_type: c.Cli.MessageTypes | None,
        expected_marker: str,
    ) -> None:
        cli.display_message("payload text", message_type)

        out = capsys.readouterr().out
        tm.that(out, has="payload text")
        tm.that(out, has=expected_marker)

    # ── display_text ──────────────────────────────────────────────────

    @pytest.mark.parametrize("style", ["bold red", "dim", None])
    def test_display_text_emits_text_regardless_of_style(
        self, capsys: Capture, style: str | None
    ) -> None:
        if style is not None:
            cli.display_text("visible words", style=style)
        else:
            cli.display_text("visible words")

        tm.that(capsys.readouterr().out, has="visible words")

    def test_display_text_is_repeatable(self, capsys: Capture) -> None:
        cli.display_text("echo")
        cli.display_text("echo")

        tm.that(capsys.readouterr().out.count("echo"), eq=2)

    # ── print_message ─────────────────────────────────────────────────

    @pytest.mark.parametrize("style", ["bold red", None])
    def test_print_message_emits_message_with_or_without_style(
        self, capsys: Capture, style: str | None
    ) -> None:
        cli.print_message("raw message", style)

        tm.that(capsys.readouterr().out, has="raw message")

    # ── display_header ────────────────────────────────────────────────

    @pytest.mark.parametrize("label", ["Setup", "Results", "Done"])
    def test_display_header_renders_label_in_rule(
        self, capsys: Capture, label: str
    ) -> None:
        cli.display_header(label)

        tm.that(capsys.readouterr().out, has=label)

    # ── display_progress ──────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("current", "total", "expected_counter"),
        [(3, 10, "[03/10]"), (5, 5, "[5/5]"), (1, 100, "[001/100]"), (0, 8, "[0/8]")],
    )
    def test_display_progress_zero_pads_counter_to_total_width(
        self, capsys: Capture, current: int, total: int, expected_counter: str
    ) -> None:
        cli.display_progress(current, total, "Processing")

        out = capsys.readouterr().out
        tm.that(out, has=expected_counter)
        tm.that(out, has="Processing")

    def test_display_progress_appends_detail_when_present(
        self, capsys: Capture
    ) -> None:
        cli.display_progress(3, 10, "Steps", detail="loading")

        tm.that(capsys.readouterr().out, has="loading")

    def test_display_progress_omits_detail_when_empty(self, capsys: Capture) -> None:
        cli.display_progress(3, 10, "Steps")

        out = capsys.readouterr().out.strip()
        assert out.endswith("Steps")

    # ── display_status ────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("success", "expected_symbol"), [(True, "✓"), (False, "✗")]
    )
    def test_display_status_symbol_reflects_outcome(
        self, capsys: Capture, success: bool, expected_symbol: str
    ) -> None:
        cli.display_status(success, "lint", "clean")

        out = capsys.readouterr().out
        tm.that(out, has=expected_symbol)
        tm.that(out, has="lint")
        tm.that(out, has="clean")

    @pytest.mark.parametrize(
        ("elapsed", "expected_timing"), [(1.23, "(1.23s)"), (0.5, "(0.50s)")]
    )
    def test_display_status_formats_elapsed_to_two_decimals(
        self, capsys: Capture, elapsed: float, expected_timing: str
    ) -> None:
        cli.display_status(True, "build", "ok", elapsed=elapsed)

        tm.that(capsys.readouterr().out, has=expected_timing)

    def test_display_status_omits_timing_when_elapsed_absent(
        self, capsys: Capture
    ) -> None:
        cli.display_status(True, "build", "ok")

        tm.that(capsys.readouterr().out, lacks="s)")

    # ── display_summary ───────────────────────────────────────────────

    def test_display_summary_reports_all_counters(self, capsys: Capture) -> None:
        cli.display_summary("Run Summary", total=10, success=8, failed=2)

        out = capsys.readouterr().out
        tm.that(out, has="Run Summary")
        tm.that(out, has="Total: 10")
        tm.that(out, has="Success: 8")
        tm.that(out, has="Failed: 2")
        tm.that(out, has="Skipped: 0")

    def test_display_summary_reflects_explicit_skipped(self, capsys: Capture) -> None:
        cli.display_summary("Summary", total=10, success=7, failed=1, skipped=2)

        tm.that(capsys.readouterr().out, has="Skipped: 2")

    # ── display_gate ──────────────────────────────────────────────────

    def test_display_gate_passed_shows_success_symbol_and_name(
        self, capsys: Capture
    ) -> None:
        cli.display_gate("ruff", True)

        out = capsys.readouterr().out
        tm.that(out, has="✓")
        tm.that(out, has="ruff")

    def test_display_gate_failed_shows_failure_symbol_name_and_message(
        self, capsys: Capture
    ) -> None:
        cli.display_gate("pyrefly", False, message="2 errors")

        out = capsys.readouterr().out
        tm.that(out, has="✗")
        tm.that(out, has="pyrefly")
        tm.that(out, has="2 errors")

    # ── display_metrics ───────────────────────────────────────────────

    def test_display_metrics_emits_each_key_value_pair(self, capsys: Capture) -> None:
        cli.display_metrics({"total": 100, "passed": 95, "failed": 5})

        out = capsys.readouterr().out
        tm.that(out, has="total=100")
        tm.that(out, has="passed=95")
        tm.that(out, has="failed=5")

    def test_display_metrics_empty_mapping_emits_nothing(self, capsys: Capture) -> None:
        cli.display_metrics({})

        tm.that(capsys.readouterr().out, eq="")

    # ── display_debug ─────────────────────────────────────────────────

    def test_display_debug_is_noop_when_not_verbose(self, capsys: Capture) -> None:
        cli.display_debug("hidden", verbose=False)

        tm.that(capsys.readouterr().out, eq="")

    def test_display_debug_emits_labelled_line_when_verbose(
        self, capsys: Capture
    ) -> None:
        cli.display_debug("visible", verbose=True)

        out = capsys.readouterr().out
        tm.that(out, has="DEBUG")
        tm.that(out, has="visible")


__all__: list[str] = ["TestsFlextCliServicesOutputCov"]
