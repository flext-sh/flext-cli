"""CLI formatter helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
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

from flext_cli import c, m
from flext_cli._utilities import FlextCliUtilitiesOutput, FlextCliUtilitiesTables


class FlextCliUtilitiesFormatters:
    """Plain-text formatter helpers for CLI services."""

    @staticmethod
    def _styled(message: str, style: str | None) -> str:
        code = c.Cli.FORMATTER_ANSI_BY_STYLE.get(style or "", "")
        return f"{code}{message}{c.Cli.FORMATTER_ANSI_RESET}" if code else message

    @classmethod
    def formatters_print(
        cls,
        message: str,
        style: str | None = None,
        *,
        error: bool = False,
    ) -> None:
        """Print one message with the optional canonical style.

        Args:
            message: Message text printed as one complete line.
            style: Optional canonical style name applying the matched ANSI wrap.
            error: Route the line to stderr instead of stdout.

        """
        FlextCliUtilitiesOutput.emit_raw(
            f"{cls._styled(message, style)}\n",
            error=error,
        )

    @classmethod
    def formatters_render_rule(cls, text: str) -> None:
        """Render one horizontal rule with the label centered between glyph runs.

        Args:
            text: Label text surrounded by spaces inside the glyph runs.

        """
        glyphs = c.Cli.FORMATTER_PANEL_GLYPH * c.Cli.FORMATTER_RULE_GLYPH_RUN
        label = f" {text} " if text else " "
        FlextCliUtilitiesOutput.emit_raw(f"{glyphs}{label}{glyphs}\n")

    @classmethod
    def formatters_render_panel(cls, content: str, *, title: str = "") -> None:
        """Render one bordered panel with an optional title line.

        Args:
            content: Panel body rendered between the border lines.
            title: Optional bold title rendered in the top border.

        """
        border = c.Cli.FORMATTER_PANEL_GLYPH * c.Cli.FORMATTER_RULE_GLYPH_RUN
        if title:
            header = f"{border} {title} {border}"
            FlextCliUtilitiesOutput.emit_raw(
                f"{cls._styled(header, c.Cli.MessageStyles.BOLD)}\n",
            )
        else:
            FlextCliUtilitiesOutput.emit_raw(f"{border}\n")
        FlextCliUtilitiesOutput.emit_raw(f"{content}\n")
        FlextCliUtilitiesOutput.emit_raw(f"{border}\n")

    @classmethod
    def formatters_render_table(cls, request: m.Cli.TableRenderRequest) -> None:
        """Render one table from the validated render request.

        Args:
            request: Typed rows, columns, and optional table title.

        """
        rendered = FlextCliUtilitiesTables.tables_render(
            request.rows,
            m.Cli.TableConfig(
                headers=tuple(request.columns),
                title=request.title or None,
            ),
        )
        FlextCliUtilitiesOutput.emit_raw(f"{rendered.unwrap()}\n")


__all__: list[str] = ["FlextCliUtilitiesFormatters"]
