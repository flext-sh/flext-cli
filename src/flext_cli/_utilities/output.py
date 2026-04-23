"""CLI output helpers shared through ``u.Cli``."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from flext_cli import c


class _SummaryStats(Protocol):
    verb: str
    total: int
    success: int
    failed: int
    skipped: int
    elapsed: float


class _ProjectFailureInfo(Protocol):
    project: str
    elapsed: float
    error_count: int
    log_path: Path
    max_show: int
    errors: Sequence[str]


class FlextCliUtilitiesOutput:
    """Output normalization helpers for message formatting."""

    @staticmethod
    def output_resolve_message_type(
        message_type: c.Cli.MessageTypes | None,
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
        message_type: c.Cli.MessageTypes | None,
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

    @staticmethod
    def emit_raw(text: str) -> None:
        """Write raw text to stdout."""
        _ = sys.stdout.write(text)
        _ = sys.stdout.flush()

    @classmethod
    def info(cls, msg: str) -> None:
        cls.emit_raw(f"INFO: {msg}\n")

    @classmethod
    def error(cls, msg: str, detail: str | None = None) -> None:
        cls.emit_raw(f"ERROR: {msg}\n")
        if detail:
            cls.emit_raw(f"  {detail}\n")

    @classmethod
    def warning(cls, msg: str) -> None:
        cls.emit_raw(f"WARN: {msg}\n")

    @classmethod
    def debug(cls, msg: str) -> None:
        cls.emit_raw(f"DEBUG: {msg}\n")

    @classmethod
    def header(cls, title: str) -> None:
        line = "=" * 60
        cls.emit_raw(f"\n{line}\n  {title}\n{line}\n")

    @classmethod
    def progress(cls, idx: int, total: int, proj: str, verb: str) -> None:
        width = len(str(total))
        cls.emit_raw(f"[{idx:0{width}d}/{total:0{width}d}] {proj} {verb} ...\n")

    @classmethod
    def status(cls, verb: str, proj: str, *, result: bool, elapsed: float) -> None:
        symbol = "[OK]" if result else "[FAIL]"
        cls.emit_raw(f"  {symbol} {verb:<8} {proj:<24} {elapsed:.2f}s\n")

    @classmethod
    def summary(cls, stats: _SummaryStats) -> None:
        verb = str(getattr(stats, "verb", "summary"))
        total = int(getattr(stats, "total", 0))
        success = int(getattr(stats, "success", 0))
        failed = int(getattr(stats, "failed", 0))
        skipped = int(getattr(stats, "skipped", 0))
        elapsed = float(getattr(stats, "elapsed", 0.0))
        cls.emit_raw(
            f"\n-- {verb} summary --\n"
            f"Total: {total}  Success: {success}  Failed: {failed}  "
            f"Skipped: {skipped}  ({elapsed:.2f}s)\n"
        )

    @classmethod
    def gate_result(
        cls,
        gate: str,
        count: int,
        *,
        passed: bool,
        elapsed: float,
    ) -> None:
        symbol = "[OK]" if passed else "[FAIL]"
        cls.emit_raw(f"    {symbol} {gate:<10} {count:>5} errors  ({elapsed:.2f}s)\n")

    @classmethod
    def project_failure(cls, info: _ProjectFailureInfo) -> None:
        project = str(getattr(info, "project", "unknown"))
        elapsed = int(getattr(info, "elapsed", 0))
        error_count = int(getattr(info, "error_count", 0))
        log_path = str(getattr(info, "log_path", ""))
        max_show = int(getattr(info, "max_show", 0))
        errors = tuple(getattr(info, "errors", ()))
        count_label = f"  [{error_count} errors]" if error_count > 0 else ""
        cls.emit_raw(
            f"  [FAIL] {project} completed in {elapsed}s{count_label}  ({log_path})\n"
        )
        for line in errors[:max_show]:
            cls.emit_raw(f"      {line}\n")
        remaining = error_count - max_show
        if remaining > 0:
            cls.emit_raw(f"      ... and {remaining} more (see log)\n")

    @staticmethod
    def get_report_dir(workspace_root: Path | str, scope: str, verb: str) -> Path:
        """Build standardized report directory path."""
        root_path = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )
        base = root_path / ".reports"
        if scope == "workspace":
            return (base / "workspace" / verb).resolve()
        return (base / verb).resolve()

    @staticmethod
    def get_report_path(
        workspace_root: Path | str,
        scope: str,
        verb: str,
        filename: str,
    ) -> Path:
        """Build standardized report file path."""
        return (
            FlextCliUtilitiesOutput.get_report_dir(workspace_root, scope, verb)
            / filename
        )


__all__: list[str] = ["FlextCliUtilitiesOutput"]
