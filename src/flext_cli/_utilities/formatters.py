"""CLI formatter fallback helpers shared through ``u.Cli``."""

from __future__ import annotations

import sys
from collections.abc import (
    Sequence,
)
from typing import ClassVar

from rich.console import Console
from rich.errors import ConsoleError, StyleError
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli import c, p, r, t


class FlextCliUtilitiesFormatters:
    """Fallback logging/output helpers for formatter services."""

    _console: ClassVar[t.Cli.RichConsoleType] = Console()

    @classmethod
    def formatters_create_tree(
        cls,
        label: str,
        logger: p.Logger,
    ) -> p.Result[t.Cli.RichTreeType]:
        """Create one Rich tree using centralized error handling."""
        try:
            return r[t.Cli.RichTreeType].ok(RichTree(label))
        except ConsoleError as exc:
            cls.formatters_log_fallback(
                logger,
                "rich_tree_creation_failed",
                exc,
                label=label,
            )
            return r[t.Cli.RichTreeType].fail(
                c.Cli.ERR_TREE_CREATION_FAILED.format(error=exc),
            )

    @classmethod
    def formatters_print(
        cls,
        message: str,
        logger: p.Logger,
        style: str | None = None,
    ) -> None:
        """Print one message via Rich with centralized fallback path."""
        try:
            cls._console.print(message, style=style)
        except (ConsoleError, StyleError) as exc:
            cls.formatters_log_fallback(
                logger,
                "rich_print_fallback",
                exc,
                message_length=len(message),
            )
            cls.formatters_write_stdout(f"{message}\n")

    @classmethod
    def formatters_render_rule(
        cls,
        text: str,
        logger: p.Logger,
    ) -> None:
        """Render one horizontal rule via Rich with fallback output."""
        try:
            cls._console.rule(text)
        except (ConsoleError, StyleError) as exc:
            cls.formatters_log_fallback(
                logger,
                "rich_rule_fallback",
                exc,
            )
            cls.formatters_write_stdout(cls.formatters_rule_fallback_text(text))

    @classmethod
    def formatters_render_panel(
        cls,
        content: str,
        logger: p.Logger,
        *,
        title: str = "",
    ) -> None:
        """Render one panel via Rich with fallback output."""
        try:
            cls._console.print(Panel(content, title=title or None))
        except (ConsoleError, StyleError) as exc:
            cls.formatters_log_fallback(
                logger,
                "rich_panel_fallback",
                exc,
            )
            cls.formatters_write_stdout(
                cls.formatters_panel_fallback_text(content, title=title),
            )

    @classmethod
    def formatters_render_table(
        cls,
        columns: t.StrSequence,
        rows: Sequence[t.StrSequence],
        logger: p.Logger,
        *,
        title: str = "",
    ) -> None:
        """Render one table via Rich with fallback output."""
        try:
            table = RichTable(title=title or None)
            for col in columns:
                table.add_column(col)
            for row in rows:
                table.add_row(*row)
            cls._console.print(table)
        except (ConsoleError, StyleError) as exc:
            cls.formatters_log_fallback(
                logger,
                "rich_table_fallback",
                exc,
            )
            cls.formatters_write_stdout(
                cls.formatters_table_fallback_text(columns, rows),
            )

    @staticmethod
    def formatters_write_stdout(text: str) -> None:
        """Write one text block directly to stdout."""
        _ = sys.stdout.write(text)
        _ = sys.stdout.flush()

    @staticmethod
    def formatters_log_fallback(
        logger: p.Logger,
        event: str,
        exc: Exception,
        **context: t.JsonPayload,
    ) -> None:
        """Emit one normalized fallback warning event."""
        if not context:
            logger.warning(event, error=str(exc))
            return
        logger.warning(
            event,
            error=str(exc),
            context=str(dict(context)),
        )

    @staticmethod
    def formatters_rule_fallback_text(text: str) -> str:
        """Build fallback text for horizontal rule rendering."""
        return f"{'=' * 60}\n  {text}\n{'=' * 60}\n"

    @staticmethod
    def formatters_panel_fallback_text(content: str, title: str = "") -> str:
        """Build fallback text for panel rendering."""
        header = f"── {title} ──\n" if title else ""
        return f"{header}{content}\n"

    @staticmethod
    def formatters_table_fallback_text(
        columns: t.StrSequence,
        rows: Sequence[t.StrSequence],
    ) -> str:
        """Build fallback text for table rendering."""
        lines: list[str] = ["  ".join(columns)]
        lines.extend("  ".join(row) for row in rows)
        return "\n".join(lines) + "\n"


__all__: list[str] = ["FlextCliUtilitiesFormatters"]
