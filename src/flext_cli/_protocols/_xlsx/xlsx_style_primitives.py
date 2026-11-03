# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_style_primitives
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    pass


class FlextCliProtocolsXlsxXlsxStylePrimitives:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxRgbColor(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["rgb"]:
            """Color kind."""
            ...

        @property
        def value(self) -> str:
            """RGB or ARGB value."""
            ...

        @property
        def tint(self) -> float:
            """Color tint."""
            ...

    @runtime_checkable
    class XlsxIndexedColor(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["indexed"]:
            """Color kind."""
            ...

        @property
        def value(self) -> int:
            """Indexed color value."""
            ...

        @property
        def tint(self) -> float:
            """Color tint."""
            ...

    @runtime_checkable
    class XlsxThemeColor(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["theme"]:
            """Color kind."""
            ...

        @property
        def value(self) -> int:
            """Theme color value."""
            ...

        @property
        def tint(self) -> float:
            """Color tint."""
            ...

    @runtime_checkable
    class XlsxAutomaticColor(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["auto"]:
            """Color kind."""
            ...

        @property
        def tint(self) -> float:
            """Color tint."""
            ...

    @runtime_checkable
    class XlsxFontSpec(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str | None:
            """Font family."""
            ...

        @property
        def size(self) -> float | None:
            """Font size."""
            ...

        @property
        def bold(self) -> bool | None:
            """Bold font state."""
            ...

        @property
        def italic(self) -> bool | None:
            """Italic font state."""
            ...

        @property
        def strike(self) -> bool | None:
            """Strike font state."""
            ...

        @property
        def outline(self) -> bool | None:
            """Outline font state."""
            ...

        @property
        def shadow(self) -> bool | None:
            """Shadow font state."""
            ...

        @property
        def condense(self) -> bool | None:
            """Condensed font state."""
            ...

        @property
        def extend(self) -> bool | None:
            """Extended font state."""
            ...

        @property
        def underline(
            self,
        ) -> Literal["single", "double", "singleAccounting", "doubleAccounting"] | None:
            """Underline style."""
            ...

        @property
        def vertical_align(
            self,
        ) -> Literal["superscript", "subscript", "baseline"] | None:
            """Vertical font alignment."""
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
            """Optional font color."""
            ...

        @property
        def charset(self) -> int | None:
            """Font charset."""
            ...

        @property
        def family(self) -> float | None:
            """Font family class."""
            ...

        @property
        def scheme(self) -> Literal["major", "minor"] | None:
            """Theme font scheme."""
            ...

    type XlsxColor = (
        XlsxRgbColor | XlsxIndexedColor | XlsxThemeColor | XlsxAutomaticColor
    )


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStylePrimitives",
]
