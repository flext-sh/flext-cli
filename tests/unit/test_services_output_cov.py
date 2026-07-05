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
from tests.constants import c

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
        assert "payload text" in out
        assert expected_marker in out

    # ── display_text ──────────────────────────────────────────────────

    @pytest.mark.parametrize("style", ["bold red", "dim", None])
    def test_display_text_emits_text_regardless_of_style(
        self,
        capsys: Capture,
        style: str | None,
    ) -> None:
        if style is not None:
            cli.display_text("visible words", style=style)
        else:
            cli.display_text("visible words")

        assert "visible words" in capsys.readouterr().out

    def test_display_text_is_repeatable(self, capsys: Capture) -> None:
        cli.display_text("echo")
        cli.display_text("echo")

        assert capsys.readouterr().out.count("echo") == 2

    # ── print_message ─────────────────────────────────────────────────

    @pytest.mark.parametrize("style", ["bold red", None])
    def test_print_message_emits_message_with_or_without_style(
        self,
        capsys: Capture,
        style: str | None,
    ) -> None:
        cli.print_message("raw message", style)

        assert "raw message" in capsys.readouterr().out

    # ── display_header ────────────────────────────────────────────────

    @pytest.mark.parametrize("label", ["Setup", "Results", "Done"])
    def test_display_header_renders_label_in_rule(
        self,
        capsys: Capture,
        label: str,
    ) -> None:
        cli.display_header(label)

        assert label in capsys.readouterr().out

    # ── display_progress ──────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("current", "total", "expected_counter"),
        [
            (3, 10, "[03/10]"),
            (5, 5, "[5/5]"),
            (1, 100, "[001/100]"),
            (0, 8, "[0/8]"),
        ],
    )
    def test_display_progress_zero_pads_counter_to_total_width(
        self,
        capsys: Capture,
        current: int,
        total: int,
        expected_counter: str,
    ) -> None:
        cli.display_progress(current, total, "Processing")

        out = capsys.readouterr().out
        assert expected_counter in out
        assert "Processing" in out

    def test_display_progress_appends_detail_when_present(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_progress(3, 10, "Steps", detail="loading")

        assert "loading" in capsys.readouterr().out

    def test_display_progress_omits_detail_when_empty(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_progress(3, 10, "Steps")

        out = capsys.readouterr().out.strip()
        assert out.endswith("Steps")

    # ── display_status ────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("success", "expected_symbol"),
        [(True, "✓"), (False, "✗")],
    )
    def test_display_status_symbol_reflects_outcome(
        self,
        capsys: Capture,
        success: bool,
        expected_symbol: str,
    ) -> None:
        cli.display_status(success, "lint", "clean")

        out = capsys.readouterr().out
        assert expected_symbol in out
        assert "lint" in out
        assert "clean" in out

    @pytest.mark.parametrize(
        ("elapsed", "expected_timing"),
        [(1.23, "(1.23s)"), (0.5, "(0.50s)")],
    )
    def test_display_status_formats_elapsed_to_two_decimals(
        self,
        capsys: Capture,
        elapsed: float,
        expected_timing: str,
    ) -> None:
        cli.display_status(True, "build", "ok", elapsed=elapsed)

        assert expected_timing in capsys.readouterr().out

    def test_display_status_omits_timing_when_elapsed_absent(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_status(True, "build", "ok")

        assert "s)" not in capsys.readouterr().out

    # ── display_summary ───────────────────────────────────────────────

    def test_display_summary_reports_all_counters(self, capsys: Capture) -> None:
        cli.display_summary("Run Summary", total=10, success=8, failed=2)

        out = capsys.readouterr().out
        assert "Run Summary" in out
        assert "Total: 10" in out
        assert "Success: 8" in out
        assert "Failed: 2" in out
        assert "Skipped: 0" in out

    def test_display_summary_reflects_explicit_skipped(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_summary("Summary", total=10, success=7, failed=1, skipped=2)

        assert "Skipped: 2" in capsys.readouterr().out

    # ── display_gate ──────────────────────────────────────────────────

    def test_display_gate_passed_shows_success_symbol_and_name(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_gate("ruff", True)

        out = capsys.readouterr().out
        assert "✓" in out
        assert "ruff" in out

    def test_display_gate_failed_shows_failure_symbol_name_and_message(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_gate("pyrefly", False, message="2 errors")

        out = capsys.readouterr().out
        assert "✗" in out
        assert "pyrefly" in out
        assert "2 errors" in out

    # ── display_metrics ───────────────────────────────────────────────

    def test_display_metrics_emits_each_key_value_pair(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_metrics({"total": 100, "passed": 95, "failed": 5})

        out = capsys.readouterr().out
        assert "total=100" in out
        assert "passed=95" in out
        assert "failed=5" in out

    def test_display_metrics_empty_mapping_emits_nothing(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_metrics({})

        assert capsys.readouterr().out == ""

    # ── display_debug ─────────────────────────────────────────────────

    def test_display_debug_is_noop_when_not_verbose(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_debug("hidden", verbose=False)

        assert capsys.readouterr().out == ""

    def test_display_debug_emits_labelled_line_when_verbose(
        self,
        capsys: Capture,
    ) -> None:
        cli.display_debug("visible", verbose=True)

        out = capsys.readouterr().out
        assert "DEBUG" in out
        assert "visible" in out


__all__: list[str] = ["TestsFlextCliServicesOutputCov"]
