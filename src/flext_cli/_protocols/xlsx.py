"""Public-shape protocols for the private XLSX byte boundary.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import p


from typing import Protocol, runtime_checkable

from flext_cli._protocols import (
    FlextCliProtocolsXlsxArchive,
    FlextCliProtocolsXlsxRules,
    FlextCliProtocolsXlsxSnapshot,
    FlextCliProtocolsXlsxWorkbook,
)

if TYPE_CHECKING:
    # mro-j47u (codex): p -> m stays type-only through the canonical facade.
    from flext_core import p


class FlextCliProtocolsXlsx(
    FlextCliProtocolsXlsxArchive,
    FlextCliProtocolsXlsxSnapshot,
    FlextCliProtocolsXlsxWorkbook,
    FlextCliProtocolsXlsxRules,
):
    """Consumer protocols for plans, requests, results, and services."""

    # NOTE (multi-agent, mro-j2yt.1): protocol properties retain the exact
    # source model objects; no dump, mapping, or adapter DTO is introduced.
    @runtime_checkable
    class XlsxSheetPlan(Protocol):
        @property
        def name(self) -> str:
            """Name of the sheet the plan targets."""
            ...

    @runtime_checkable
    class XlsxWorkbookPlan(Protocol):
        @property
        def sheets(self) -> tuple[p.Cli.XlsxSheetPlan, ...]:
            """Ordered sheet plans composing the workbook."""
            ...

        @property
        def full_calculation_on_load(self) -> bool:
            """Whether the workbook forces full calculation on load."""
            ...

    @runtime_checkable
    class XlsxRenderRequest(Protocol):
        @property
        def template(self) -> bytes | None:
            """Optional workbook template bytes used as the render base."""
            ...

        @property
        def plan(self) -> p.Cli.XlsxWorkbookPlan:
            """Workbook plan describing the render target."""
            ...

    @runtime_checkable
    class XlsxRenderResult(Protocol):
        @property
        def content(self) -> bytes:
            """Rendered workbook bytes."""
            ...

        @property
        def plan(self) -> p.Cli.XlsxWorkbookPlan:
            """Workbook plan the render produced."""
            ...

    @runtime_checkable
    class XlsxParseRangeRequest(Protocol):
        @property
        def reference(self) -> str:
            """Cell range reference in A1 notation."""
            ...

    # mro-j2yt.1 (xlsx_reference_api): public structural formatting boundary.
    @runtime_checkable
    class XlsxFormatReferenceRequest(Protocol):
        @property
        def area(self) -> p.Cli.XlsxCellRange:
            """Cell range the reference formats."""
            ...

        @property
        def sheet(self) -> str | None:
            """Optional sheet name qualifying the reference."""
            ...

        @property
        def absolute(self) -> bool:
            """Whether the reference uses absolute column and row anchors."""
            ...

        @property
        def collapse_single_cell(self) -> bool:
            """Whether a single-cell range collapses to one address."""
            ...

    @runtime_checkable
    class XlsxReference(Protocol):
        @property
        def reference(self) -> str:
            """Formatted reference text."""
            ...

    @runtime_checkable
    class XlsxArchiveInspectionRequest(Protocol):
        @property
        def source(self) -> bytes:
            """Workbook bytes the operation inspects."""
            ...

        @property
        def policy(self) -> p.Cli.XlsxArchivePolicy:
            """Archive inspection policy applied to the source bytes."""
            ...

    @runtime_checkable
    class XlsxStyleCatalogRequest(Protocol):
        @property
        def source(self) -> bytes:
            """Workbook bytes the catalog extracts styles from."""
            ...

        @property
        def style_name_prefix(self) -> str:
            """Prefix applied to every generated style name."""
            ...

    @runtime_checkable
    class XlsxStyleTemplateRequest(XlsxStyleCatalogRequest, Protocol): ...

    @runtime_checkable
    class XlsxStyleMapEntry(Protocol):
        @property
        def source_style_id(self) -> int:
            """Source style identifier the entry maps from."""
            ...

        @property
        def style_name(self) -> str:
            """Generated style name the entry maps to."""
            ...

    @runtime_checkable
    class XlsxStyleTemplateResult(Protocol):
        @property
        def content(self) -> bytes:
            """Rendered template workbook bytes."""
            ...

        @property
        def style_map(self) -> tuple[p.Cli.XlsxStyleMapEntry, ...]:
            """Mapping of source style identifiers to generated style names."""
            ...

    @runtime_checkable
    class XlsxService(FlextCliProtocolsXlsxSnapshot.XlsxSnapshotService, Protocol):
        def xlsx_parse_range(
            self,
            request: FlextCliProtocolsXlsx.XlsxParseRangeRequest,
        ) -> p.Result[p.Cli.XlsxCellRange]:
            """Parse one cell range reference from the request."""
            ...

        def xlsx_format_reference(
            self,
            request: FlextCliProtocolsXlsx.XlsxFormatReferenceRequest,
        ) -> p.Result[p.Cli.XlsxReference]:
            """Format one cell range reference from the request."""
            ...

        def xlsx_render(
            self,
            request: FlextCliProtocolsXlsx.XlsxRenderRequest,
        ) -> p.Result[p.Cli.XlsxRenderResult]:
            """Render workbook bytes according to the request plan."""
            ...

        def xlsx_inspect(
            self,
            request: FlextCliProtocolsXlsx.XlsxArchiveInspectionRequest,
        ) -> p.Result[p.Cli.XlsxArchiveInspection]:
            """Inspect the workbook archive described by the request."""
            ...

        def xlsx_style_catalog(
            self,
            request: FlextCliProtocolsXlsx.XlsxStyleCatalogRequest,
        ) -> p.Result[p.Cli.XlsxStyleCatalog]:
            """Extract the style catalog from the request workbook bytes."""
            ...

        def xlsx_style_template(
            self,
            request: FlextCliProtocolsXlsx.XlsxStyleTemplateRequest,
        ) -> p.Result[p.Cli.XlsxStyleTemplateResult]:
            """Render a styled template from the request catalog."""
            ...

        def xlsx_recalc(
            self,
            request: p.Cli.XlsxRecalcRequest,
        ) -> p.Result[p.Cli.XlsxRecalcResult]:
            """Recalculate workbook bytes through the request contract."""
            ...

        def xlsx_recalc_parity(
            self,
            request: p.Cli.XlsxRecalcParityRequest,
        ) -> p.Result[p.Cli.XlsxRecalcParityReport]:
            """Validate recalculation parity for the request inputs."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsXlsx",)
