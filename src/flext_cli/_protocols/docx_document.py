# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/docx_document
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart05

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._protocols import FlextCliProtocolsDocxStyles


class FlextCliProtocolsDocxDocument:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class DocxRunPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def text(self) -> str:
            """Run text."""
            ...

        @property
        def style(self) -> FlextCliProtocolsDocxStyles.DocxRunStyleSpec:
            """Run style specification."""
            ...

    @runtime_checkable
    class DocxParagraphPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def runs(self) -> tuple[FlextCliProtocolsDocxDocument.DocxRunPlan, ...]:
            """Paragraph runs."""
            ...

        @property
        def style(self) -> str | None:
            """Named paragraph style."""
            ...

        @property
        def style_spec(
            self,
        ) -> FlextCliProtocolsDocxStyles.DocxParagraphStyleSpec | None:
            """Inline paragraph style specification."""
            ...

        @property
        def alignment(self) -> str | None:
            """Paragraph alignment override."""
            ...

    @runtime_checkable
    class DocxTableCellPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def paragraphs(
            self,
        ) -> tuple[FlextCliProtocolsDocxDocument.DocxParagraphPlan, ...]:
            """Cell paragraphs."""
            ...

    @runtime_checkable
    class DocxTableRowPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def cells(self) -> tuple[FlextCliProtocolsDocxDocument.DocxTableCellPlan, ...]:
            """Row cells."""
            ...

    @runtime_checkable
    class DocxTablePlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def rows(self) -> tuple[FlextCliProtocolsDocxDocument.DocxTableRowPlan, ...]:
            """Table rows."""
            ...

        @property
        def style(self) -> str | None:
            """Named table style."""
            ...

    @runtime_checkable
    class DocxSectionPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def width(self) -> float | None:
            """Page width in EMU."""
            ...

        @property
        def height(self) -> float | None:
            """Page height in EMU."""
            ...

        @property
        def orientation(self) -> str:
            """Page orientation."""
            ...

        @property
        def left_margin(self) -> float | None:
            """Left margin in EMU."""
            ...

        @property
        def right_margin(self) -> float | None:
            """Right margin in EMU."""
            ...

        @property
        def top_margin(self) -> float | None:
            """Top margin in EMU."""
            ...

        @property
        def bottom_margin(self) -> float | None:
            """Bottom margin in EMU."""
            ...

    @runtime_checkable
    class DocxDocumentPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def paragraphs(
            self,
        ) -> tuple[FlextCliProtocolsDocxDocument.DocxParagraphPlan, ...]:
            """Document paragraphs."""
            ...

        @property
        def tables(self) -> tuple[FlextCliProtocolsDocxDocument.DocxTablePlan, ...]:
            """Document tables."""
            ...

        @property
        def sections(self) -> tuple[FlextCliProtocolsDocxDocument.DocxSectionPlan, ...]:
            """Document sections."""
            ...

        @property
        def core_properties(self) -> t.JsonMapping:
            """Core document properties."""
            ...

    @runtime_checkable
    class DocxRenderRequest(
        FlextCliProtocolsBaseFlextclimodelsbasePart05.OfficeRenderRequest, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def plan(self) -> FlextCliProtocolsDocxDocument.DocxDocumentPlan:
            """Validated document plan."""
            ...

        @property
        def source_date_epoch(self) -> int | None:
            """Deterministic build epoch in seconds since 1970."""
            ...

    @runtime_checkable
    class DocxRenderResult(
        FlextCliProtocolsBaseFlextclimodelsbasePart05.OfficeRenderResult, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def plan(self) -> FlextCliProtocolsDocxDocument.DocxDocumentPlan:
            """Exact source plan."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsDocxDocument",
]
