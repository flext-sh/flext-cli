# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_style_primitives
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxStylePrimitives:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxRgbColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["rgb"]: ...
        @property
        def value(self) -> str: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class XlsxIndexedColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["indexed"]: ...
        @property
        def value(self) -> int: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class XlsxThemeColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["theme"]: ...
        @property
        def value(self) -> int: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class XlsxAutomaticColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["auto"]: ...
        @property
        def tint(self) -> float: ...

    @runtime_checkable
    class XlsxFontSpec(Protocol):
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
        def strike(self) -> bool | None: ...
        @property
        def outline(self) -> bool | None: ...
        @property
        def shadow(self) -> bool | None: ...
        @property
        def condense(self) -> bool | None: ...
        @property
        def extend(self) -> bool | None: ...
        @property
        def underline(
            self,
        ) -> (
            Literal["single", "double", "singleAccounting", "doubleAccounting"] | None
        ): ...
        @property
        def vertical_align(
            self,
        ) -> Literal["superscript", "subscript", "baseline"] | None: ...
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
        @property
        def charset(self) -> int | None: ...
        @property
        def family(self) -> float | None: ...
        @property
        def scheme(self) -> Literal["major", "minor"] | None: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStylePrimitives",
]
