"""CLI output payload builders shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, t


class FlextCliUtilitiesOutputPayloads:
    """Build output text and styles without writing to process streams."""

    @staticmethod
    def output_resolve_message_type(
        message_type: c.Cli.MessageTypes | None,
    ) -> c.Cli.MessageTypes:
        """Resolve one message type to canonical enum value.

        Returns:
            The resulting ``c.Cli.MessageTypes``.

        """
        return (
            message_type
            if message_type is not None
            else c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE
        )

    @staticmethod
    def output_resolve_style(style: str | None) -> str:
        """Resolve print style with canonical empty-style fallback.

        Returns:
            The resulting ``str``.

        """
        return style if style is not None else c.Cli.OUTPUT_EMPTY_STYLE

    @staticmethod
    def output_message_payload(
        message: str,
        message_type: c.Cli.MessageTypes | None,
    ) -> t.Pair[str, str]:
        """Build one canonical display payload and style from message type.

        Returns:
            The resulting ``t.Pair[str, str]``.

        """
        final_type = FlextCliUtilitiesOutputPayloads.output_resolve_message_type(
            message_type,
        )
        default_type = c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE
        style = c.Cli.MESSAGE_STYLE_MAP.get(
            final_type,
            c.Cli.MESSAGE_STYLE_MAP[default_type],
        )
        emoji = c.Cli.MESSAGE_EMOJI_MAP.get(
            final_type,
            c.Cli.MESSAGE_EMOJI_MAP[default_type],
        )
        return f"{emoji} {message}", style

    @staticmethod
    def output_progress_line(
        current: int,
        total: int,
        label: str,
        *,
        detail: str,
    ) -> str:
        """Build one canonical progress line text.

        Returns:
            The resulting ``str``.

        """
        width = len(str(total))
        suffix = f" {detail}" if detail else ""
        return f"[{current:0{width}d}/{total}] {label}{suffix}"

    @staticmethod
    def output_summary_content(
        *,
        total: int,
        success: int,
        failed: int,
        skipped: int,
    ) -> str:
        """Build one canonical summary content string.

        Returns:
            The resulting ``str``.

        """
        return (
            f"Total: {total}  Success: {success}  Failed: {failed}  Skipped: {skipped}"
        )

    @staticmethod
    def output_debug_line(message: str) -> t.Pair[str, str]:
        """Build one canonical debug line and style.

        Returns:
            The resulting ``t.Pair[str, str]``.

        """
        return f"[{c.Cli.OUTPUT_LOG_LEVEL_DEBUG}] {message}", c.Cli.MessageStyles.DIM

    @staticmethod
    def output_table_error(error_message: str | None) -> t.Pair[str, str]:
        """Build one canonical table error line and style.

        Returns:
            The resulting ``t.Pair[str, str]``.

        """
        error = error_message or c.Cli.ERR_UNKNOWN_ERROR
        return f"{c.Cli.OUTPUT_TABLE_ERROR_LABEL} {error}", c.Cli.MessageStyles.BOLD_RED

    @staticmethod
    def output_status_line(
        label: str,
        detail: str,
        *,
        success: bool,
        elapsed: float | None,
    ) -> t.Pair[str, str]:
        """Build one canonical status line and style.

        Returns:
            The resulting ``t.Pair[str, str]``.

        """
        symbol = c.Cli.SYMBOL_SUCCESS_MARK if success else c.Cli.SYMBOL_FAILURE_MARK
        style = (
            c.Cli.MessageStyles.BOLD_GREEN if success else c.Cli.MessageStyles.BOLD_RED
        )
        timing = f"  ({elapsed:.2f}s)" if elapsed is not None else ""
        line = f"  {symbol} {label:<8} {detail:<24}{timing}"
        return line, style

    @staticmethod
    def output_gate_line(name: str, *, passed: bool, message: str) -> t.Pair[str, str]:
        """Build one canonical gate line and style.

        Returns:
            The resulting ``t.Pair[str, str]``.

        """
        symbol = c.Cli.SYMBOL_SUCCESS_MARK if passed else c.Cli.SYMBOL_FAILURE_MARK
        style = (
            c.Cli.MessageStyles.BOLD_GREEN if passed else c.Cli.MessageStyles.BOLD_RED
        )
        suffix = f"  {message}" if message else ""
        return f"    {symbol} {name:<10}{suffix}", style


__all__: list[str] = ["FlextCliUtilitiesOutputPayloads"]
