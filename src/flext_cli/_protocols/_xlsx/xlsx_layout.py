# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_layout
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxLayout:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxMergePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> p.Cli.XlsxCellRange: ...

    @runtime_checkable
    class XlsxCommentPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def at(self) -> p.Cli.XlsxCellAddress: ...
        @property
        def text(self) -> str: ...
        @property
        def author(self) -> str: ...
        @property
        def width(self) -> int | None: ...
        @property
        def height(self) -> int | None: ...

    @runtime_checkable
    class XlsxExternalHyperlinkPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["external"]: ...
        @property
        def at(self) -> p.Cli.XlsxCellAddress: ...
        @property
        def target(self) -> str: ...

    @runtime_checkable
    class XlsxNavigationHyperlinkPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["navigation"]: ...
        @property
        def at(self) -> p.Cli.XlsxCellAddress: ...
        @property
        def destination_sheet(self) -> str: ...
        @property
        def destination(self) -> p.Cli.XlsxCellAddress: ...

    @runtime_checkable
    class XlsxDimensionPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def axis(self) -> Literal["row", "column"]: ...
        @property
        def first(self) -> int: ...
        @property
        def last(self) -> int: ...
        @property
        def size(self) -> float | None: ...
        @property
        def hidden(self) -> bool: ...

    @runtime_checkable
    class XlsxGroupPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def axis(self) -> Literal["row", "column"]: ...
        @property
        def first(self) -> int: ...
        @property
        def last(self) -> int: ...
        @property
        def outline_level(self) -> int: ...
        @property
        def hidden(self) -> bool: ...

    @runtime_checkable
    class XlsxFreezePanePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def at(self) -> p.Cli.XlsxCellAddress: ...

    @runtime_checkable
    class XlsxAutoFilterPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> p.Cli.XlsxCellRange: ...

    @runtime_checkable
    class XlsxViewPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def visibility(self) -> Literal["visible", "hidden", "veryHidden"]: ...
        @property
        def tab_color(self) -> str | None: ...

    @runtime_checkable
    class XlsxSheetLayoutPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def merges(self) -> tuple[p.Cli.XlsxMergePlan, ...]: ...
        @property
        def comments(self) -> tuple[p.Cli.XlsxCommentPlan, ...]: ...
        @property
        def hyperlinks(
            self,
        ) -> tuple[
            Annotated[
                p.Cli.XlsxExternalHyperlinkPlan | p.Cli.XlsxNavigationHyperlinkPlan,
                m.Field(discriminator="kind"),
            ],
            ...,
        ]: ...
        @property
        def dimensions(self) -> tuple[p.Cli.XlsxDimensionPlan, ...]: ...
        @property
        def groups(self) -> tuple[p.Cli.XlsxGroupPlan, ...]: ...
        @property
        def freeze_pane(self) -> p.Cli.XlsxFreezePanePlan | None: ...
        @property
        def auto_filter(self) -> p.Cli.XlsxAutoFilterPlan | None: ...
        @property
        def view(self) -> p.Cli.XlsxViewPlan | None: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxLayout",
]
