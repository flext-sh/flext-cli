"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import ClassVar, Literal, Self, overload, override

from rich.console import Console
from rich.errors import ConsoleError, StyleError
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli import FlextCliServiceBase, c, t
from flext_core import r


class FlextCliFormatters(FlextCliServiceBase):
    """Thin Rich formatters facade - delegates to Rich library directly.

    Business Rules:
    ───────────────
    1. This is ONE OF TWO files allowed to import Rich directly
    2. All formatting operations MUST delegate to Rich library (no reimplementation)
    3. Console output MUST respect no_color configuration flag
    4. All operations MUST return r[T] for error handling
    5. Rich Console MUST be initialized once per instance (singleton pattern)
    6. Formatting operations MUST not modify input data (immutable)
    7. Error handling MUST catch Rich exceptions and return r failures

    ZERO TOLERANCE: Use Rich directly, minimal wrapper only for CLI abstraction.
    """

    class Tree:
        """Wrapper around Rich Tree; add() returns None by default (optional return via overload).

        Use add(label) for side-effect only; add(label, return_child=True) to chain.
        """

        def __init__(self, tree: RichTree) -> None:
            """Wrap a Rich Tree instance for side-effect-safe usage."""
            self._tree: RichTree = tree

        @overload
        def add(self, label: str) -> None: ...

        @overload
        def add(self, label: str, *, return_child: Literal[True]) -> Self: ...

        def add(
            self,
            label: str,
            *,
            return_child: bool = False,
        ) -> FlextCliFormatters.Tree | None:
            """Add a child node; return the wrapped child only when *return_child* is set."""
            child = self._tree.add(label)
            return FlextCliFormatters.Tree(child) if return_child else None

        @override
        def __str__(self) -> str:
            return str(self._tree)

        @property
        def tree(self) -> RichTree:
            """Expose inner Rich Tree for rendering or advanced use."""
            return self._tree

    console: ClassVar[Console] = Console()

    @classmethod
    def create_tree(cls, label: str) -> r[FlextCliFormatters.Tree]:
        """Create Rich tree wrapped for optional return use (add() returns None by default).

        Args:
            label: Tree root label

        Returns:
            r[FlextCliFormatters.Tree]: Wrapper instance or error

        Note:
            Use tree.add(label) for side-effect; tree.add(label, return_child=True) to chain.

        """
        try:
            tree = RichTree(label)
            return r[FlextCliFormatters.Tree].ok(FlextCliFormatters.Tree(tree))
        except ConsoleError as exc:
            cls._get_or_create_logger().warning(
                "rich_tree_creation_failed",
                error=str(exc),
                label=label,
            )
            return r[FlextCliFormatters.Tree].fail(
                c.Cli.FormattersErrorMessages.TREE_CREATION_FAILED.format(error=exc),
            )

    @classmethod
    def print(cls, message: str, style: str | None = None) -> None:
        """Print formatted message using Rich.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")

        Note:
            For advanced Rich features, access self.console directly.

        """
        try:
            cls.console.print(message, style=style)
        except (ConsoleError, StyleError) as exc:
            cls._get_or_create_logger().warning(
                "rich_print_fallback",
                error=str(exc),
                message_length=len(message),
            )
            _ = sys.stdout.write(f"{message}\n")
            _ = sys.stdout.flush()

    @classmethod
    def render_rule(cls, text: str) -> None:
        """Render a horizontal rule with centered text via Rich."""
        try:
            cls.console.rule(text)
        except (ConsoleError, StyleError) as exc:
            cls._get_or_create_logger().warning(
                "rich_rule_fallback",
                error=str(exc),
            )
            _ = sys.stdout.write(f"{'=' * 60}\n  {text}\n{'=' * 60}\n")
            _ = sys.stdout.flush()

    @classmethod
    def render_panel(cls, content: str, *, title: str = "") -> None:
        """Render a Rich Panel with optional title."""
        try:
            cls.console.print(Panel(content, title=title or None))
        except (ConsoleError, StyleError) as exc:
            cls._get_or_create_logger().warning(
                "rich_panel_fallback",
                error=str(exc),
            )
            header = f"── {title} ──\n" if title else ""
            _ = sys.stdout.write(f"{header}{content}\n")
            _ = sys.stdout.flush()

    @classmethod
    def render_table(
        cls,
        columns: t.StrSequence,
        rows: Sequence[t.StrSequence],
        *,
        title: str = "",
    ) -> None:
        """Render a Rich Table with columns and rows."""
        try:
            table = RichTable(title=title or None)
            for col in columns:
                table.add_column(col)
            for row in rows:
                table.add_row(*row)
            cls.console.print(table)
        except (ConsoleError, StyleError) as exc:
            cls._get_or_create_logger().warning(
                "rich_table_fallback",
                error=str(exc),
            )
            header = "  ".join(columns)
            _ = sys.stdout.write(f"{header}\n")
            for row in rows:
                _ = sys.stdout.write(f"{'  '.join(row)}\n")
            _ = sys.stdout.flush()


__all__ = ["FlextCliFormatters"]
