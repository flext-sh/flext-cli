"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliFormatters, c, s, t, u


class FlextCliOutput(s):
    """CLI output tools for the flext ecosystem.

    Provides a unified output API while delegating to specialized
    abstraction layers:

    - FlextCliFormatters: Rich-based visual output (tables, progress, styling)
    - Built-in: JSON, YAML, CSV formatting

    """

    # ── Static methods (public API) ─────────────────────────────────

    @staticmethod
    def display_message(
        message: str,
        message_type: t.Cli.MessageTypeLiteral | c.Cli.MessageTypes | None = None,
    ) -> None:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        """
        payload, style = u.Cli.output_message_payload(message, message_type)
        FlextCliOutput.print_message(payload, style=style)

    @staticmethod
    def display_text(text: str, *, style: str | None = None) -> None:
        """Display text with optional style. Delegates to print_message."""
        FlextCliOutput.print_message(text, style=style)

    @staticmethod
    def print_message(message: str, style: str | None = None) -> None:
        """Print a message using FlextCliFormatters."""
        validated_style = u.Cli.output_resolve_style(style)
        FlextCliFormatters.print(message, style=validated_style)

    @staticmethod
    def display_header(text: str) -> None:
        """Display a section header via Rich rule."""
        FlextCliFormatters.render_rule(text)

    @staticmethod
    def display_progress(
        current: int,
        total: int,
        label: str,
        *,
        detail: str = "",
    ) -> None:
        """Display progress indicator [current/total] label detail."""
        FlextCliFormatters.print(
            u.Cli.output_progress_line(current, total, label, detail=detail)
        )

    @staticmethod
    def display_status(
        success: bool,
        label: str,
        detail: str,
        *,
        elapsed: float | None = None,
    ) -> None:
        """Display a pass/fail status line."""
        line, style = u.Cli.output_status_line(
            success,
            label,
            detail,
            elapsed=elapsed,
        )
        FlextCliFormatters.print(line, style=style)

    @staticmethod
    def display_summary(
        title: str,
        *,
        total: int,
        success: int,
        failed: int,
        skipped: int = 0,
    ) -> None:
        """Display a summary panel."""
        content = u.Cli.output_summary_content(
            total=total,
            success=success,
            failed=failed,
            skipped=skipped,
        )
        FlextCliFormatters.render_panel(content, title=title)

    @staticmethod
    def display_gate(name: str, passed: bool, *, message: str = "") -> None:
        """Display a quality gate result."""
        line, style = u.Cli.output_gate_line(name, passed, message=message)
        FlextCliFormatters.print(line, style=style)

    @staticmethod
    def display_metrics(
        metrics: t.ConfigValueMapping,
    ) -> None:
        """Display key=value metric pairs."""
        for key, value in metrics.items():
            FlextCliFormatters.print(f"{key}={value}")

    @staticmethod
    def display_debug(message: str, *, verbose: bool = False) -> None:
        """Display debug message (no-op unless verbose)."""
        if not verbose:
            return
        line, style = u.Cli.output_debug_line(message)
        FlextCliFormatters.print(line, style=style)


__all__ = ["FlextCliOutput"]
