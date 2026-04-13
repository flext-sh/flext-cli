"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Self, overload, override

from flext_cli import FlextCliServiceBase, t, u
from flext_core import p, r


class FlextCliFormatters(FlextCliServiceBase):
    """Thin Rich formatters facade - delegates to Rich library directly."""

    class Tree:
        """Wrapper around Rich Tree; add() returns None by default (optional return via overload).

        Use add(label) for side-effect only; add(label, return_child=True) to chain.
        """

        def __init__(self, tree: t.Cli.RichTreeType) -> None:
            """Wrap a Rich Tree instance for side-effect-safe usage."""
            self._tree: t.Cli.RichTreeType = tree

        @overload
        def add(self, label: str) -> None: ...

        @overload
        def add(
            self, label: str, *, return_child: t.Cli.ReturnChildLiteral
        ) -> Self: ...

        def add(
            self,
            label: str,
            *,
            return_child: bool = False,
        ) -> Self | None:
            """Add a child node; return the wrapped child only when *return_child* is set."""
            child = self._tree.add(label)
            return self.__class__(child) if return_child else None

        @override
        def __str__(self) -> str:
            return str(self._tree)

        @property
        def tree(self) -> t.Cli.RichTreeType:
            """Expose inner Rich Tree for rendering or advanced use."""
            return self._tree

    @classmethod
    def create_tree(cls, label: str) -> p.Result[FlextCliFormatters.Tree]:
        """Create Rich tree wrapped for optional return use (add() returns None by default).

        Args:
            label: Tree root label

        Returns:
            r[FlextCliFormatters.Tree]: Wrapper instance or error

        Note:
            Use tree.add(label) for side-effect; tree.add(label, return_child=True) to chain.

        """
        tree_result = u.Cli.formatters_create_tree(
            label,
            cls._get_or_create_logger(),
        )
        if tree_result.failure:
            return r[FlextCliFormatters.Tree].fail_op(
                "create cli tree",
                tree_result.error or "Tree creation failed",
            )
        return r[FlextCliFormatters.Tree].ok(FlextCliFormatters.Tree(tree_result.value))

    @classmethod
    def print(cls, message: str, style: str | None = None) -> None:
        """Print formatted message using Rich.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")

        Note:
            For advanced Rich features, access self.console directly.

        """
        u.Cli.formatters_print(
            message,
            cls._get_or_create_logger(),
            style=style,
        )

    @classmethod
    def render_rule(cls, text: str) -> None:
        """Render a horizontal rule with centered text via Rich."""
        u.Cli.formatters_render_rule(text, cls._get_or_create_logger())

    @classmethod
    def render_panel(cls, content: str, *, title: str = "") -> None:
        """Render a Rich Panel with optional title."""
        u.Cli.formatters_render_panel(
            content,
            cls._get_or_create_logger(),
            title=title,
        )

    @classmethod
    def render_table(
        cls,
        columns: t.StrSequence,
        rows: Sequence[t.StrSequence],
        *,
        title: str = "",
    ) -> None:
        """Render a Rich Table with columns and rows."""
        u.Cli.formatters_render_table(
            columns,
            rows,
            cls._get_or_create_logger(),
            title=title,
        )


__all__: list[str] = ["FlextCliFormatters"]
