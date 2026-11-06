# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_style_fills
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxStylePrimitives


class FlextCliProtocolsXlsxXlsxStyleFills:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxPatternFillSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["pattern"]:
            """Fill kind."""
            ...

        @property
        def pattern(
            self,
        ) -> (
            Literal[
                "solid",
                "darkDown",
                "darkGray",
                "darkGrid",
                "darkHorizontal",
                "darkTrellis",
                "darkUp",
                "darkVertical",
                "gray0625",
                "gray125",
                "lightDown",
                "lightGray",
                "lightGrid",
                "lightHorizontal",
                "lightTrellis",
                "lightUp",
                "lightVertical",
                "mediumGray",
            ]
            | None
        ):
            """Fill pattern."""
            ...

        @property
        def foreground(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxRgbColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxIndexedColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxThemeColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxAutomaticColor
            | None
        ):
            """Optional foreground color."""
            ...

        @property
        def background(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxRgbColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxIndexedColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxThemeColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxAutomaticColor
            | None
        ):
            """Optional background color."""
            ...

    @runtime_checkable
    class XlsxGradientStop(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def color(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxRgbColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxIndexedColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxThemeColor
            | FlextCliProtocolsXlsxXlsxStylePrimitives.XlsxAutomaticColor
        ):
            """Gradient stop color."""
            ...

        @property
        def position(self) -> float:
            """Gradient stop position."""
            ...

    @runtime_checkable
    class XlsxGradientFillSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["gradient"]:
            """Fill kind."""
            ...

        @property
        def mode(self) -> Literal["linear", "path"]:
            """Gradient mode."""
            ...

        @property
        def degree(self) -> float:
            """Linear gradient angle."""
            ...

        @property
        def left(self) -> float:
            """Path left extent."""
            ...

        @property
        def right(self) -> float:
            """Path right extent."""
            ...

        @property
        def top(self) -> float:
            """Path top extent."""
            ...

        @property
        def bottom(self) -> float:
            """Path bottom extent."""
            ...

        @property
        def stops(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxStyleFills.XlsxGradientStop, ...]:
            """Ordered gradient stops."""
            ...

    type XlsxFillSpec = XlsxPatternFillSpec | XlsxGradientFillSpec


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStyleFills",
]
