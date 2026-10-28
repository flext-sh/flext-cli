"""CLI output and formatting tools.

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

from collections.abc import MutableSequence

from flext_cli import c, p, s, u
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


__all__: MutableSequence[str] = ["FlextCliOutput"]
