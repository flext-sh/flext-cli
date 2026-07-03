"""CLI output helpers shared through ``u.Cli``."""

from __future__ import annotations

import sys

from flext_cli import c, t


class FlextCliUtilitiesOutput:
    """Implementation part for FlextCliUtilitiesOutput."""

    @staticmethod
    def output_resolve_message_type(
        message_type: c.Cli.MessageTypes | None,
    ) -> c.Cli.MessageTypes:
        """Resolve one message type to canonical enum value."""
        return (
            message_type
            if message_type is not None
            else c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE
        )

    @staticmethod
    def output_resolve_style(style: str | None) -> str:
        """Resolve print style with canonical empty-style fallback."""
        return style if style is not None else c.Cli.OUTPUT_EMPTY_STYLE

    @staticmethod
    def output_message_payload(
        message: str,
        message_type: c.Cli.MessageTypes | None,
    ) -> t.Pair[str, str]:
        """Build one canonical display payload and style from message type."""
        final_type = FlextCliUtilitiesOutput.output_resolve_message_type(message_type)
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
        """Build one canonical progress line text."""
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
        """Build one canonical summary content string."""
        return (
            f"Total: {total}  Success: {success}  Failed: {failed}  Skipped: {skipped}"
        )

    @staticmethod
    def output_debug_line(message: str) -> t.Pair[str, str]:
        """Build one canonical debug line and style."""
        return f"[{c.Cli.OUTPUT_LOG_LEVEL_DEBUG}] {message}", c.Cli.MessageStyles.DIM

    @staticmethod
    def output_table_error(error_message: str | None) -> t.Pair[str, str]:
        """Build one canonical table error line and style."""
        error = error_message or c.Cli.ERR_UNKNOWN_ERROR
        return f"{c.Cli.OUTPUT_TABLE_ERROR_LABEL} {error}", c.Cli.MessageStyles.BOLD_RED

    @staticmethod
    def emit_raw(text: str) -> None:
        """Write raw text to stdout."""
        _ = sys.stdout.write(text)
        _ = sys.stdout.flush()

    @classmethod
    def info(cls, msg: str) -> None:
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_INFO}: {msg}\n")

    @classmethod
    def error(cls, msg: str, detail: str | None = None) -> None:
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_ERROR}: {msg}\n")
        if detail:
            cls.emit_raw(f"  {detail}\n")

    @classmethod
    def warning(cls, msg: str) -> None:
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_WARNING}: {msg}\n")

    @classmethod
    def debug(cls, msg: str) -> None:
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_DEBUG}: {msg}\n")

    @classmethod
    def header(cls, title: str) -> None:
        line = "=" * c.Cli.OUTPUT_HEADER_RULE_WIDTH
        cls.emit_raw(f"\n{line}\n  {title}\n{line}\n")

    @classmethod
    def progress(cls, idx: int, total: int, proj: str, verb: str) -> None:
        width = len(str(total))
        cls.emit_raw(f"[{idx:0{width}d}/{total:0{width}d}] {proj} {verb} ...\n")


__all__: list[str] = ["FlextCliUtilitiesOutput"]
