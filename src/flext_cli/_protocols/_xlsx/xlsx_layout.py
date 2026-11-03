# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_layout
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxCells


class FlextCliProtocolsXlsxXlsxLayout:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxMergePlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Merged cell range."""
            ...

    @runtime_checkable
    class XlsxCommentPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def at(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Comment cell."""
            ...

        @property
        def text(self) -> str:
            """Comment text."""
            ...

        @property
        def author(self) -> str:
            """Comment author."""
            ...

        @property
        def width(self) -> int | None:
            """Comment width."""
            ...

        @property
        def height(self) -> int | None:
            """Comment height."""
            ...

    @runtime_checkable
    class XlsxExternalHyperlinkPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["external"]:
            """Hyperlink kind."""
            ...

        @property
        def at(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Hyperlink cell."""
            ...

        @property
        def target(self) -> str:
            """External hyperlink target."""
            ...

    @runtime_checkable
    class XlsxNavigationHyperlinkPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["navigation"]:
            """Hyperlink kind."""
            ...

        @property
        def at(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Hyperlink cell."""
            ...

        @property
        def destination_sheet(self) -> str:
            """Destination worksheet."""
            ...

        @property
        def destination(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Destination address."""
            ...

    @runtime_checkable
    class XlsxDimensionPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def axis(self) -> Literal["row", "column"]:
            """Dimension axis."""
            ...

        @property
        def first(self) -> int:
            """First index."""
            ...

        @property
        def last(self) -> int:
            """Last index."""
            ...

        @property
        def size(self) -> float | None:
            """Explicit size."""
            ...

        @property
        def hidden(self) -> bool:
            """Hidden state."""
            ...

    @runtime_checkable
    class XlsxGroupPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def axis(self) -> Literal["row", "column"]:
            """Grouped axis."""
            ...

        @property
        def first(self) -> int:
            """First index."""
            ...

        @property
        def last(self) -> int:
            """Last index."""
            ...

        @property
        def outline_level(self) -> int:
            """Outline level."""
            ...

        @property
        def hidden(self) -> bool:
            """Hidden state."""
            ...

    @runtime_checkable
    class XlsxFreezePanePlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def at(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """First scrolling cell."""
            ...

    @runtime_checkable
    class XlsxAutoFilterPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Auto-filter range."""
            ...

    @runtime_checkable
    class XlsxViewPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def visibility(self) -> Literal["visible", "hidden", "veryHidden"]:
            """Worksheet visibility."""
            ...

        @property
        def tab_color(self) -> str | None:
            """RGB or ARGB tab color."""
            ...

    @runtime_checkable
    class XlsxSheetLayoutPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def merges(self) -> tuple[FlextCliProtocolsXlsxXlsxLayout.XlsxMergePlan, ...]:
            """Merged ranges."""
            ...

        @property
        def comments(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxLayout.XlsxCommentPlan, ...]:
            """Cell comments."""
            ...

        @property
        def hyperlinks(
            self,
        ) -> tuple[
            FlextCliProtocolsXlsxXlsxLayout.XlsxExternalHyperlinkPlan
            | FlextCliProtocolsXlsxXlsxLayout.XlsxNavigationHyperlinkPlan,
            ...,
        ]:
            """Cell hyperlinks."""
            ...

        @property
        def dimensions(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxLayout.XlsxDimensionPlan, ...]:
            """Row and column dimensions."""
            ...

        @property
        def groups(self) -> tuple[FlextCliProtocolsXlsxXlsxLayout.XlsxGroupPlan, ...]:
            """Row and column groups."""
            ...

        @property
        def freeze_pane(
            self,
        ) -> FlextCliProtocolsXlsxXlsxLayout.XlsxFreezePanePlan | None:
            """Optional freeze pane."""
            ...

        @property
        def auto_filter(
            self,
        ) -> FlextCliProtocolsXlsxXlsxLayout.XlsxAutoFilterPlan | None:
            """Optional auto-filter."""
            ...

        @property
        def view(self) -> FlextCliProtocolsXlsxXlsxLayout.XlsxViewPlan | None:
            """Optional worksheet view."""
            ...

    type XlsxHyperlinkPlan = XlsxExternalHyperlinkPlan | XlsxNavigationHyperlinkPlan


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxLayout",
]
