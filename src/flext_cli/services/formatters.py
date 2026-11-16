"""FLEXT CLI Formatters - plain-text rendering facade.

Provides minimal CLI formatting abstraction for the command surface.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence

from flext_cli import c, m, p, s, u


class FlextCliFormatters(s[p.Cli.RuntimeStatus]):
    """Plain-text formatters facade for the CLI command surface."""

    @classmethod
    def display_message(
        cls,
        message: str,
        message_type: c.Cli.MessageTypes | None = None,
    ) -> None:
        """Display one message with the marker and style of its type.

        Args:
            message: Message to display.
            message_type: Message type (info, success, error, warning); the
                default type applies when omitted.

        """
        payload, style = u.Cli.output_message_payload(message, message_type)
        cls.print(
            payload,
            style=style,
            error=message_type == c.Cli.MessageTypes.ERROR,
        )

    @classmethod
    def display_progress(
        cls,
        current: int,
        total: int,
        label: str,
        *,
        detail: str = "",
    ) -> None:
        """Display one progress line with a zero-padded counter.

        Args:
            current: Completed step count.
            total: Total step count.
            label: Short label describing the work in progress.
            detail: Optional trailing detail appended to the line.

        """
        cls.print(u.Cli.output_progress_line(current, total, label, detail=detail))

    @classmethod
    def print(
        cls,
        message: str,
        style: str | None = None,
        *,
        error: bool = False,
    ) -> None:
        """Print one message with the optional style.

        Args:
            message: Message to print.
            style: Optional style name applied to the message.
            error: Whether the message prints to the error stream.

        """
        u.Cli.formatters_print(message, style=style, error=error)

    @classmethod
    def render_rule(cls, text: str) -> None:
        """Render a horizontal rule with centered text.

        Args:
            text: Text centered within the rule.

        """
        u.Cli.formatters_render_rule(text)

    @classmethod
    def render_panel(cls, content: str, *, title: str = "") -> None:
        """Render a bordered panel with an optional title.

        Args:
            content: Panel body content.
            title: Optional panel title.

        """
        u.Cli.formatters_render_panel(content, title=title)

    @classmethod
    def render_table(
        cls,
        columns: Sequence[str],
        rows: Sequence[Sequence[str]],
        *,
        title: str = "",
    ) -> None:
        """Render a table with columns and rows.

        Args:
            columns: Ordered column headers.
            rows: Ordered rows of cells aligned with the columns.
            title: Optional table title.

        """
        u.Cli.formatters_render_table(
            m.Cli.TableRenderRequest(columns=columns, rows=rows, title=title),
        )


__all__: MutableSequence[str] = ["FlextCliFormatters"]
