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

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

import pytest

from flext_cli import cli
from tests import c, tm


class TestsFlextCliServicesOutputCov:
    """Observable-behavior tests for the FlextCliOutput display contract."""

    # ── display_message ───────────────────────────────────────────────

    @staticmethod
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
        capsys: pytest.CaptureFixture[str],
        message_type: c.Cli.MessageTypes | None,
        expected_marker: str,
    ) -> None:
        """Verify that display message prefixes type marker and keeps text."""
        cli.display_message("payload text", message_type)

        captured = capsys.readouterr()
        out = captured.err if message_type == c.Cli.MessageTypes.ERROR else captured.out
        tm.that(out, has="payload text")
        tm.that(out, has=expected_marker)
        tm.that(
            captured.out if message_type == c.Cli.MessageTypes.ERROR else captured.err,
            eq="",
        )

    # ── display_text ──────────────────────────────────────────────────

    @staticmethod
    @pytest.mark.parametrize("style", ["bold red", "dim", None])
    def test_display_text_emits_text_regardless_of_style(
        capsys: pytest.CaptureFixture[str],
        style: str | None,
    ) -> None:
        """Verify that display text emits text regardless of style."""
        if style is not None:
            cli.display_text("visible words", style=style)
        else:
            cli.display_text("visible words")

        tm.that(capsys.readouterr().out, has="visible words")

    @staticmethod
    def test_display_text_is_repeatable(capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that display text is repeatable."""
        cli.display_text("echo")
        cli.display_text("echo")

        tm.that(capsys.readouterr().out.count("echo"), eq=2)

    # ── print_message ─────────────────────────────────────────────────

    @staticmethod
    @pytest.mark.parametrize("style", ["bold red", None])
    def test_print_message_emits_message_with_or_without_style(
        capsys: pytest.CaptureFixture[str],
        style: str | None,
    ) -> None:
        """Verify that print message emits message with or without style."""
        cli.print_message("raw message", style)

        tm.that(capsys.readouterr().out, has="raw message")

    # ── display_progress ──────────────────────────────────────────────

    @staticmethod
    @pytest.mark.parametrize(
        ("current", "total", "expected_counter"),
        [(3, 10, "[03/10]"), (5, 5, "[5/5]"), (1, 100, "[001/100]"), (0, 8, "[0/8]")],
    )
    def test_display_progress_zero_pads_counter_to_total_width(
        capsys: pytest.CaptureFixture[str],
        current: int,
        total: int,
        expected_counter: str,
    ) -> None:
        """Verify that display progress zero pads counter to total width."""
        cli.display_progress(current, total, "Processing")

        out = capsys.readouterr().out
        tm.that(out, has=expected_counter)
        tm.that(out, has="Processing")

    @staticmethod
    def test_display_progress_appends_detail_when_present(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Verify that display progress appends detail when present."""
        cli.display_progress(3, 10, "Steps", detail="loading")

        tm.that(capsys.readouterr().out, has="loading")

    @staticmethod
    def test_display_progress_omits_detail_when_empty(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Verify that display progress omits detail when empty."""
        cli.display_progress(3, 10, "Steps")

        out = capsys.readouterr().out.strip()
        tm.ok(out.endswith("Steps"))
