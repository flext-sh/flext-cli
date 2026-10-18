"""CLI output and formatting tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys

from flext_cli import c, p, s, t, u
from flext_cli.services import FlextCliFormatters


class FlextCliOutput(s[p.Cli.RuntimeStatus]):
    """CLI output tools for the flext ecosystem.

    Provides a unified output API while delegating to specialized
    abstraction layers:

    - FlextCliFormatters: Rich-based visual output (tables, progress, styling)
    - Built-in: JSON, YAML, CSV formatting

    """

    # ── Static methods (public API) ─────────────────────────────────

    @staticmethod
    def emit_stdout(text: str, *, end: str = "\n") -> None:
        """Emit exact machine-readable text without Rich interpretation.

        Args:
            text: Raw text to write to stdout.
            end: Trailing text appended after the payload.

        """
        _ = sys.stdout.write(f"{text}{end}")

    @staticmethod
    def display_message(
        message: str,
        message_type: c.Cli.MessageTypes | None = None,
    ) -> None:
        """Display message with specified type and styling.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        """
        payload, style = u.Cli.output_message_payload(message, message_type)
        FlextCliFormatters.print(
            payload,
            style=style,
            error=message_type == c.Cli.MessageTypes.ERROR,
        )

    @staticmethod
    def display_text(text: str, *, style: str | None = None) -> None:
        """Display text with optional style. Delegates to print_message.

        Args:
            text: Text to display.
            style: Optional Rich style name; the default style applies when
                omitted.

        """
        FlextCliOutput.print_message(text, style=style)

    @staticmethod
    def display_message_plain(
        message: str,
        message_type: c.Cli.MessageTypes | None = None,
    ) -> None:
        """Display message bypassing Rich styling for large machine-readable text.

        Args:
            message: Message to display
            message_type: Optional type used only for a plain text prefix

        """
        prefix = ""
        if message_type == c.Cli.MessageTypes.ERROR:
            prefix = "[ERROR] "
        elif message_type == c.Cli.MessageTypes.WARNING:
            prefix = "[WARN] "
        elif message_type == c.Cli.MessageTypes.SUCCESS:
            prefix = "[OK] "
        elif message_type == c.Cli.MessageTypes.INFO:
            prefix = "[INFO] "
        u.Cli.emit_raw(
            f"{prefix}{message}\n",
            error=message_type == c.Cli.MessageTypes.ERROR,
        )

    @staticmethod
    def print_message(message: str, style: str | None = None) -> None:
        """Print a message using FlextCliFormatters.

        Args:
            message: Message to print.
            style: Optional Rich style name; the default style applies when
                omitted.

        """
        validated_style = u.Cli.output_resolve_style(style)
        FlextCliFormatters.print(message, style=validated_style)

    @staticmethod
    def display_header(text: str) -> None:
        """Display a section header via Rich rule.

        Args:
            text: Header text to render.

        """
        FlextCliFormatters.render_rule(text)

    @staticmethod
    def display_progress(
        current: int,
        total: int,
        label: str,
        *,
        detail: str = "",
    ) -> None:
        """Display progress indicator [current/total] label detail.

        Args:
            current: Completed step count.
            total: Total step count.
            label: Short label describing the work in progress.
            detail: Optional trailing detail appended to the line.

        """
        FlextCliFormatters.print(
            u.Cli.output_progress_line(current, total, label, detail=detail),
        )

    @staticmethod
    def display_status(
        label: str,
        detail: str,
        *,
        success: bool,
        elapsed: float | None = None,
    ) -> None:
        """Display a pass/fail status line.

        Args:
            label: Short label naming the checked item.
            detail: Descriptive detail rendered after the label.
            success: Whether the status renders as passed or failed.
            elapsed: Optional elapsed seconds appended to the line.

        """
        line, style = u.Cli.output_status_line(
            label,
            detail,
            success=success,
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
        """Display a summary panel.

        Args:
            title: Panel title.
            total: Total number of processed items.
            success: Number of successfully processed items.
            failed: Number of failed items.
            skipped: Number of skipped items.

        """
        content = u.Cli.output_summary_content(
            total=total,
            success=success,
            failed=failed,
            skipped=skipped,
        )
        FlextCliFormatters.render_panel(content, title=title)

    @staticmethod
    def display_gate(name: str, *, passed: bool, message: str = "") -> None:
        """Display a quality gate result.

        Args:
            name: Gate name.
            passed: Whether the gate passed.
            message: Optional explanatory message appended to the line.

        """
        line, style = u.Cli.output_gate_line(name, passed=passed, message=message)
        FlextCliFormatters.print(line, style=style)

    @staticmethod
    def display_metrics(metrics: t.ConfigValueMapping) -> None:
        """Display key=value metric pairs.

        Args:
            metrics: Mapping of metric names to their values.

        """
        for key, value in metrics.items():
            FlextCliFormatters.print(f"{key}={value}")

    @staticmethod
    def display_debug(message: str, *, verbose: bool = False) -> None:
        """Display debug message (no-op unless verbose).

        Args:
            message: Debug message to display.
            verbose: Whether debug output is enabled.

        """
        if not verbose:
            return
        line, style = u.Cli.output_debug_line(message)
        FlextCliFormatters.print(line, style=style)


__all__: t.MutableSequenceOf[str] = ["FlextCliOutput"]
