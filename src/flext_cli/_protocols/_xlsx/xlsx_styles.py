# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_styles
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import (
        FlextCliProtocolsXlsxXlsxStyleFills,
        FlextCliProtocolsXlsxXlsxStylePrimitives,
    )


class FlextCliProtocolsXlsxXlsxStyles:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxBorderSideSpec(FlextProtocols.BaseModel, Protocol):
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
        ):
            """Border style."""
            ...

        @property
        def color(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxRgbColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxIndexedColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxThemeColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxAutomaticColor
            | None
        ):
            """Optional border color."""
            ...

    @runtime_checkable
    class XlsxBorderSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def left(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional left border."""
            ...

        @property
        def right(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional right border."""
            ...

        @property
        def top(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional top border."""
            ...

        @property
        def bottom(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional bottom border."""
            ...

        @property
        def start(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional logical start border."""
            ...

        @property
        def end(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional logical end border."""
            ...

        @property
        def diagonal(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional diagonal border."""
            ...

        @property
        def vertical(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional internal vertical border."""
            ...

        @property
        def horizontal(
            self,
        ) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSideSpec | None:
            """Optional internal horizontal border."""
            ...

        @property
        def diagonal_up(self) -> bool:
            """Draw upward diagonal."""
            ...

        @property
        def diagonal_down(self) -> bool:
            """Draw downward diagonal."""
            ...

        @property
        def outline(self) -> bool:
            """Apply border as outline."""
            ...

    @runtime_checkable
    class XlsxAlignmentSpec(FlextProtocols.BaseModel, Protocol):
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
        ):
            """Horizontal alignment."""
            ...

        @property
        def vertical(
            self,
        ) -> Literal["top", "center", "bottom", "justify", "distributed"] | None:
            """Vertical alignment."""
            ...

        @property
        def wrap_text(self) -> bool | None:
            """Wrap cell text."""
            ...

        @property
        def shrink_to_fit(self) -> bool | None:
            """Shrink cell text."""
            ...

        @property
        def text_rotation(self) -> int:
            """Text rotation."""
            ...

        @property
        def indent(self) -> float:
            """Text indent."""
            ...

        @property
        def relative_indent(self) -> float:
            """Relative text indent."""
            ...

        @property
        def justify_last_line(self) -> bool | None:
            """Justify the final line."""
            ...

        @property
        def reading_order(self) -> float:
            """Text reading order."""
            ...

    @runtime_checkable
    class XlsxVisualStyleSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def font(self) -> FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxFontSpec:
            """Font specification."""
            ...

        @property
        def fill(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxStyleFills.XlsxPatternFillSpec
            | FlextCliProtocolsXlsxXlsxStyleFills.XlsxGradientFillSpec
        ):
            """Fill specification."""
            ...

        @property
        def border(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxBorderSpec:
            """Border specification."""
            ...

        @property
        def alignment(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxAlignmentSpec:
            """Alignment specification."""
            ...

        @property
        def number_format(self) -> str:
            """Excel number format."""
            ...

    @runtime_checkable
    class XlsxNamedStyleSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Named style key."""
            ...

        @property
        def visual(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxVisualStyleSpec:
            """Protection-free visual signature."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStyles",
]
