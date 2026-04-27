"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence

from flext_cli import FlextCliServiceBase, p, t, u


class FlextCliFormatters(FlextCliServiceBase):
    """Thin Rich formatters facade - delegates to Rich library directly."""

    @classmethod
    def create_tree(cls, label: str) -> p.Result[t.Cli.RichTreeType]:
        """Create one Rich tree via the canonical CLI utility."""
        return u.Cli.formatters_create_tree(label)

    @classmethod
    def print(cls, message: str, style: str | None = None) -> None:
        """Print formatted message using Rich."""
        u.Cli.formatters_print(message, style=style)

    @classmethod
    def render_rule(cls, text: str) -> None:
        """Render a horizontal rule with centered text via Rich."""
        u.Cli.formatters_render_rule(text)

    @classmethod
    def render_panel(cls, content: str, *, title: str = "") -> None:
        """Render a Rich Panel with optional title."""
        u.Cli.formatters_render_panel(content, title=title)

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
            u.Cli.TableRenderRequest(columns=columns, rows=rows, title=title),
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliFormatters"]
