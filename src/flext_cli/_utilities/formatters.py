"""CLI formatter helpers shared through ``u.Cli``."""

from __future__ import annotations

from typing import Final

from flext_cli import c, m

from .output import FlextCliUtilitiesOutput
from .tables import FlextCliUtilitiesTables

_RESET: Final[str] = "\x1b[0m"
_ANSI_BY_STYLE: Final[dict[str, str]] = {
    c.Cli.MessageStyles.BLUE: "\x1b[34m",
    c.Cli.MessageStyles.GREEN: "\x1b[32m",
    c.Cli.MessageStyles.RED: "\x1b[31m",
    c.Cli.MessageStyles.YELLOW: "\x1b[33m",
    c.Cli.MessageStyles.CYAN: "\x1b[36m",
    c.Cli.MessageStyles.WHITE: "\x1b[37m",
    c.Cli.MessageStyles.DIM: "\x1b[2m",
    c.Cli.MessageStyles.BOLD: "\x1b[1m",
    c.Cli.MessageStyles.BOLD_BLUE: "\x1b[1;34m",
    c.Cli.MessageStyles.BOLD_GREEN: "\x1b[1;32m",
    c.Cli.MessageStyles.BOLD_RED: "\x1b[1;31m",
    c.Cli.MessageStyles.BOLD_YELLOW: "\x1b[1;33m",
}
_RULE_GLYPH_RUN: Final[int] = 4
_PANEL_GLYPH: Final[str] = "-"


class FlextCliUtilitiesFormatters:
    """Plain-text formatter helpers for CLI services."""

    @staticmethod
    def _styled(message: str, style: str | None) -> str:
        code = _ANSI_BY_STYLE.get(style or "", "")
        return f"{code}{message}{_RESET}" if code else message

    @classmethod
    def formatters_print(cls, message: str, style: str | None = None) -> None:
        """Print one message with the optional canonical style."""
        FlextCliUtilitiesOutput.emit_raw(f"{cls._styled(message, style)}\n")

    @classmethod
    def formatters_render_rule(cls, text: str) -> None:
        """Render one horizontal rule with the label centered between glyph runs."""
        glyphs = _PANEL_GLYPH * _RULE_GLYPH_RUN
        label = f" {text} " if text else " "
        FlextCliUtilitiesOutput.emit_raw(f"{glyphs}{label}{glyphs}\n")

    @classmethod
    def formatters_render_panel(cls, content: str, *, title: str = "") -> None:
        """Render one bordered panel with an optional title line."""
        border = _PANEL_GLYPH * 4
        if title:
            FlextCliUtilitiesOutput.emit_raw(
                f"{cls._styled(f'{border} {title} {border}', c.Cli.MessageStyles.BOLD)}\n"
            )
        else:
            FlextCliUtilitiesOutput.emit_raw(f"{border}\n")
        FlextCliUtilitiesOutput.emit_raw(f"{content}\n")
        FlextCliUtilitiesOutput.emit_raw(f"{border}\n")

    @classmethod
    def formatters_render_table(cls, request: m.Cli.TableRenderRequest) -> None:
        """Render one table from the validated render request."""
        rendered = FlextCliUtilitiesTables.tables_render(
            request.rows,
            m.Cli.TableConfig(
                headers=tuple(request.columns), title=request.title or None
            ),
        )
        FlextCliUtilitiesOutput.emit_raw(f"{rendered.unwrap()}\n")


__all__: list[str] = ["FlextCliUtilitiesFormatters"]
