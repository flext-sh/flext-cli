"""CLI output helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import c, t


class FlextCliUtilitiesOutput:
    """Output normalization helpers for message formatting."""

    @staticmethod
    def output_resolve_message_type(
        message_type: t.Cli.MessageTypeLiteral | c.Cli.MessageTypes | None,
    ) -> c.Cli.MessageTypes:
        """Resolve one message type to canonical enum value."""
        if message_type is None:
            return c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE
        if isinstance(message_type, str):
            try:
                return c.Cli.MessageTypes(message_type)
            except ValueError:
                return c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE
        return message_type

    @staticmethod
    def output_resolve_style(style: str | None) -> str:
        """Resolve print style with canonical empty-style fallback."""
        return style if isinstance(style, str) else c.Cli.OUTPUT_EMPTY_STYLE

    @staticmethod
    def output_message_payload(
        message: str,
        message_type: t.Cli.MessageTypeLiteral | c.Cli.MessageTypes | None,
    ) -> tuple[str, str]:
        """Build one canonical display payload and style from message type."""
        final_type = FlextCliUtilitiesOutput.output_resolve_message_type(message_type)
        style = c.Cli.MESSAGE_STYLE_MAP.get(final_type, c.Cli.MessageStyles.BLUE)
        emoji = c.Cli.MESSAGE_EMOJI_MAP.get(final_type, c.Cli.EMOJI_INFO)
        return f"{emoji} {message}", style

    @staticmethod
    def output_progress_line(
        current: int,
        total: int,
        label: str,
        *,
        detail: str,
    ) -> str:
        """Build one canonical progress line text."""
        width = len(str(total))
        suffix = f" {detail}" if detail else ""
        return f"[{current:0{width}d}/{total}] {label}{suffix}"

    @staticmethod
    def output_status_line(
        success: bool,
        label: str,
        detail: str,
        *,
        elapsed: float | None,
    ) -> tuple[str, str]:
        """Build one canonical status line and style."""
        symbol = c.Cli.SYMBOL_SUCCESS_MARK if success else c.Cli.SYMBOL_FAILURE_MARK
        style = (
            c.Cli.MessageStyles.BOLD_GREEN if success else c.Cli.MessageStyles.BOLD_RED
        )
        timing = f"  ({elapsed:.2f}s)" if elapsed is not None else ""
        line = f"  {symbol} {label:<8} {detail:<24}{timing}"
        return line, style

    @staticmethod
    def output_gate_line(name: str, passed: bool, *, message: str) -> tuple[str, str]:
        """Build one canonical gate line and style."""
        symbol = c.Cli.SYMBOL_SUCCESS_MARK if passed else c.Cli.SYMBOL_FAILURE_MARK
        style = (
            c.Cli.MessageStyles.BOLD_GREEN if passed else c.Cli.MessageStyles.BOLD_RED
        )
        suffix = f"  {message}" if message else ""
        return f"    {symbol} {name:<10}{suffix}", style

    @staticmethod
    def output_summary_content(
        *,
        total: int,
        success: int,
        failed: int,
        skipped: int,
    ) -> str:
        """Build one canonical summary content string."""
        return (
            f"Total: {total}  Success: {success}  Failed: {failed}  Skipped: {skipped}"
        )

    @staticmethod
    def output_debug_line(message: str) -> tuple[str, str]:
        """Build one canonical debug line and style."""
        return f"[DEBUG] {message}", c.Cli.MessageStyles.DIM

    @staticmethod
    def output_table_error(error_message: str | None) -> tuple[str, str]:
        """Build one canonical table error line and style."""
        error = error_message or "unknown error"
        return f"[table error] {error}", c.Cli.MessageStyles.BOLD_RED


__all__ = ["FlextCliUtilitiesOutput"]
