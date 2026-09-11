"""FLEXT CLI Formatters - plain-text rendering facade.

Provides minimal CLI formatting abstraction for the command surface.
"""

from __future__ import annotations

from flext_cli import m, s, t, u


class FlextCliFormatters(s):
    """Plain-text formatters facade for the CLI command surface."""

    @classmethod
    def print(cls, message: str, style: str | None = None) -> None:
        """Print one message with the optional style."""
        u.Cli.formatters_print(message, style=style)

    @classmethod
    def render_rule(cls, text: str) -> None:
        """Render a horizontal rule with centered text."""
        u.Cli.formatters_render_rule(text)

    @classmethod
    def render_panel(cls, content: str, *, title: str = "") -> None:
        """Render a bordered panel with an optional title."""
        u.Cli.formatters_render_panel(content, title=title)

    @classmethod
    def render_table(
        cls,
        columns: t.StrSequence,
        rows: t.SequenceOf[t.StrSequence],
        *,
        title: str = "",
    ) -> None:
        """Render a table with columns and rows."""
        u.Cli.formatters_render_table(
            m.Cli.TableRenderRequest(columns=columns, rows=rows, title=title)
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliFormatters"]
