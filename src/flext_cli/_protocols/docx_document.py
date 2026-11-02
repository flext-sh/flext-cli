# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/docx_document
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsDocxDocument:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class DocxRunPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def text(self) -> str: ...
        @property
        def style(self) -> p.Cli.DocxRunStyleSpec: ...

    @runtime_checkable
    class DocxParagraphPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def runs(self) -> tuple[p.Cli.DocxRunPlan, ...]: ...
        @property
        def style(self) -> str | None: ...
        @property
        def style_spec(self) -> p.Cli.DocxParagraphStyleSpec | None: ...
        @property
        def alignment(self) -> str | None: ...

    @runtime_checkable
    class DocxTableCellPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def paragraphs(self) -> tuple[p.Cli.DocxParagraphPlan, ...]: ...

    @runtime_checkable
    class DocxTableRowPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def cells(self) -> tuple[p.Cli.DocxTableCellPlan, ...]: ...

    @runtime_checkable
    class DocxTablePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def rows(self) -> tuple[p.Cli.DocxTableRowPlan, ...]: ...
        @property
        def style(self) -> str | None: ...

    @runtime_checkable
    class DocxSectionPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def width(self) -> float | None: ...
        @property
        def height(self) -> float | None: ...
        @property
        def orientation(self) -> str: ...
        @property
        def left_margin(self) -> float | None: ...
        @property
        def right_margin(self) -> float | None: ...
        @property
        def top_margin(self) -> float | None: ...
        @property
        def bottom_margin(self) -> float | None: ...

    @runtime_checkable
    class DocxDocumentPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def paragraphs(self) -> tuple[p.Cli.DocxParagraphPlan, ...]: ...
        @property
        def tables(self) -> tuple[p.Cli.DocxTablePlan, ...]: ...
        @property
        def sections(self) -> tuple[p.Cli.DocxSectionPlan, ...]: ...
        @property
        def core_properties(self) -> t.JsonMapping: ...

    @runtime_checkable
    class DocxRenderRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def template(self) -> bytes | None: ...
        @property
        def plan(self) -> p.Cli.DocxDocumentPlan: ...
        @property
        def source_date_epoch(self) -> int | None: ...

    @runtime_checkable
    class DocxRenderResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes: ...
        @property
        def plan(self) -> p.Cli.DocxDocumentPlan: ...


__all__: list[str] = [
    "FlextCliProtocolsDocxDocument",
]
