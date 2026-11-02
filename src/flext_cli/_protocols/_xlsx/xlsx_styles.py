# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_styles
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxStyles:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxBorderSideSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def style(
            self,
        ) -> (
            Literal[
                "dashDot",
                "dashDotDot",
                "dashed",
                "dotted",
                "double",
                "hair",
                "medium",
                "mediumDashDot",
                "mediumDashDotDot",
                "mediumDashed",
                "slantDashDot",
                "thick",
                "thin",
            ]
            | None
        ): ...
        @property
        def color(
            self,
        ) -> (
            Annotated[
                p.Cli.XlsxRgbColor
                | p.Cli.XlsxIndexedColor
                | p.Cli.XlsxThemeColor
                | p.Cli.XlsxAutomaticColor,
                m.Field(discriminator="kind"),
            ]
            | None
        ): ...

    @runtime_checkable
    class XlsxBorderSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def left(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def right(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def top(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def bottom(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def start(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def end(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def diagonal(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def vertical(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def horizontal(self) -> p.Cli.XlsxBorderSideSpec | None: ...
        @property
        def diagonal_up(self) -> bool: ...
        @property
        def diagonal_down(self) -> bool: ...
        @property
        def outline(self) -> bool: ...

    @runtime_checkable
    class XlsxAlignmentSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def horizontal(
            self,
        ) -> (
            Literal[
                "general",
                "left",
                "center",
                "right",
                "fill",
                "justify",
                "centerContinuous",
                "distributed",
            ]
            | None
        ): ...
        @property
        def vertical(
            self,
        ) -> Literal["top", "center", "bottom", "justify", "distributed"] | None: ...
        @property
        def wrap_text(self) -> bool | None: ...
        @property
        def shrink_to_fit(self) -> bool | None: ...
        @property
        def text_rotation(self) -> int: ...
        @property
        def indent(self) -> float: ...
        @property
        def relative_indent(self) -> float: ...
        @property
        def justify_last_line(self) -> bool | None: ...
        @property
        def reading_order(self) -> float: ...

    @runtime_checkable
    class XlsxVisualStyleSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def font(self) -> p.Cli.XlsxFontSpec: ...
        @property
        def fill(
            self,
        ) -> Annotated[
            p.Cli.XlsxPatternFillSpec | p.Cli.XlsxGradientFillSpec,
            m.Field(discriminator="kind"),
        ]: ...
        @property
        def border(self) -> p.Cli.XlsxBorderSpec: ...
        @property
        def alignment(self) -> p.Cli.XlsxAlignmentSpec: ...
        @property
        def number_format(self) -> str: ...

    @runtime_checkable
    class XlsxNamedStyleSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def visual(self) -> p.Cli.XlsxVisualStyleSpec: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStyles",
]
