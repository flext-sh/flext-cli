# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/docx_styles
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli._protocols import FlextCliProtocolsColor

if TYPE_CHECKING:
    pass


class FlextCliProtocolsDocxStyles:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class DocxRgbColor(FlextCliProtocolsColor.RgbColor, Protocol):
        """Structural data contract projected from the owning model."""

    @runtime_checkable
    class DocxThemeColor(FlextProtocols.BaseModel, Protocol):
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
    class DocxAutomaticColor(FlextProtocols.BaseModel, Protocol):
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
    class DocxFontSpec(FlextProtocols.BaseModel, Protocol):
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
        def underline(
            self,
        ) -> Literal["single", "double", "singleAccounting", "doubleAccounting"] | None:
            """Underline style."""
            ...

        @property
        def strike(self) -> bool | None:
            """Strike font state."""
            ...

        @property
        def color(
            self,
        ) -> (
            FlextCliProtocolsDocxStyles.DocxRgbColor
            | FlextCliProtocolsDocxStyles.DocxThemeColor
            | FlextCliProtocolsDocxStyles.DocxAutomaticColor
            | None
        ):
            """Optional font color."""
            ...

        @property
        def highlight(
            self,
        ) -> (
            Literal[
                "yellow",
                "green",
                "cyan",
                "magenta",
                "blue",
                "red",
                "darkBlue",
                "darkCyan",
                "darkGreen",
                "darkMagenta",
                "darkRed",
                "darkYellow",
                "darkGray",
                "lightGray",
                "black",
            ]
            | None
        ):
            """Optional highlight color."""
            ...

        @property
        def superscript(self) -> bool | None:
            """Superscript."""
            ...

        @property
        def subscript(self) -> bool | None:
            """Subscript."""
            ...

        @property
        def all_caps(self) -> bool | None:
            """All caps."""
            ...

        @property
        def small_caps(self) -> bool | None:
            """Small caps."""
            ...

    @runtime_checkable
    class DocxParagraphFormatSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def alignment(
            self,
        ) -> Literal["left", "center", "right", "justify", "distribute"] | None:
            """Paragraph alignment."""
            ...

        @property
        def space_before(self) -> float | None:
            """Space before."""
            ...

        @property
        def space_after(self) -> float | None:
            """Space after."""
            ...

        @property
        def line_spacing(self) -> float | None:
            """Line spacing multiplier."""
            ...

        @property
        def first_line_indent(self) -> float | None:
            """First line indent."""
            ...

        @property
        def left_indent(self) -> float | None:
            """Left indent."""
            ...

        @property
        def right_indent(self) -> float | None:
            """Right indent."""
            ...

        @property
        def keep_together(self) -> bool | None:
            """Keep together."""
            ...

        @property
        def keep_with_next(self) -> bool | None:
            """Keep with next paragraph."""
            ...

        @property
        def page_break_before(self) -> bool | None:
            """Page break before paragraph."""
            ...

        @property
        def widow_control(self) -> bool | None:
            """Widow control."""
            ...

    @runtime_checkable
    class DocxRunStyleSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def font(self) -> FlextCliProtocolsDocxStyles.DocxFontSpec | None:
            """Optional run font specification."""
            ...

    @runtime_checkable
    class DocxParagraphStyleSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def font(self) -> FlextCliProtocolsDocxStyles.DocxFontSpec | None:
            """Optional paragraph font specification."""
            ...

        @property
        def paragraph_format(
            self,
        ) -> FlextCliProtocolsDocxStyles.DocxParagraphFormatSpec | None:
            """Optional paragraph format specification."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsDocxStyles",
]
