# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/docx_styles
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsDocxStyles:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class DocxRgbColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["rgb"]: ...
        @property
        def value(self) -> str: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class DocxThemeColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["theme"]: ...
        @property
        def value(self) -> int: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class DocxAutomaticColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["auto"]: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class DocxFontSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str | None: ...
        @property
        def size(self) -> float | None: ...
        @property
        def bold(self) -> bool | None: ...
        @property
        def italic(self) -> bool | None: ...
        @property
        def underline(
            self,
        ) -> (
            Literal["single", "double", "singleAccounting", "doubleAccounting"] | None
        ): ...
        @property
        def strike(self) -> bool | None: ...
        @property
        def color(
            self,
        ) -> (
            Annotated[
                p.Cli.DocxRgbColor | p.Cli.DocxThemeColor | p.Cli.DocxAutomaticColor,
                m.Field(discriminator="kind"),
            ]
            | None
        ): ...
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
        ): ...
        @property
        def superscript(self) -> bool | None: ...
        @property
        def subscript(self) -> bool | None: ...
        @property
        def all_caps(self) -> bool | None: ...
        @property
        def small_caps(self) -> bool | None: ...

    @runtime_checkable
    class DocxParagraphFormatSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def alignment(
            self,
        ) -> Literal["left", "center", "right", "justify", "distribute"] | None: ...
        @property
        def space_before(self) -> float | None: ...
        @property
        def space_after(self) -> float | None: ...
        @property
        def line_spacing(self) -> float | None: ...
        @property
        def first_line_indent(self) -> float | None: ...
        @property
        def left_indent(self) -> float | None: ...
        @property
        def right_indent(self) -> float | None: ...
        @property
        def keep_together(self) -> bool | None: ...
        @property
        def keep_with_next(self) -> bool | None: ...
        @property
        def page_break_before(self) -> bool | None: ...
        @property
        def widow_control(self) -> bool | None: ...

    @runtime_checkable
    class DocxRunStyleSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def font(self) -> p.Cli.DocxFontSpec | None: ...

    @runtime_checkable
    class DocxParagraphStyleSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def font(self) -> p.Cli.DocxFontSpec | None: ...
        @property
        def paragraph_format(self) -> p.Cli.DocxParagraphFormatSpec | None: ...


__all__: list[str] = [
    "FlextCliProtocolsDocxStyles",
]
