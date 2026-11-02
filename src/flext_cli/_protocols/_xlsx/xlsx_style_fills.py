# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_style_fills
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxStyleFills:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxPatternFillSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["pattern"]: ...
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
        ): ...
        @property
        def foreground(
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
        def background(
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
    class XlsxGradientStop(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def color(
            self,
        ) -> Annotated[
            p.Cli.XlsxRgbColor
            | p.Cli.XlsxIndexedColor
            | p.Cli.XlsxThemeColor
            | p.Cli.XlsxAutomaticColor,
            m.Field(discriminator="kind"),
        ]: ...
        @property
        def position(self) -> float: ...

    @runtime_checkable
    class XlsxGradientFillSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["gradient"]: ...
        @property
        def mode(self) -> Literal["linear", "path"]: ...
        @property
        def degree(self) -> float: ...
        @property
        def left(self) -> float: ...
        @property
        def right(self) -> float: ...
        @property
        def top(self) -> float: ...
        @property
        def bottom(self) -> float: ...
        @property
        def stops(self) -> tuple[p.Cli.XlsxGradientStop, ...]: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStyleFills",
]
