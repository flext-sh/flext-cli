"""Public-shape protocols for the private XLSX byte boundary.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli._protocols import (
    FlextCliProtocolsXlsxArchive,
    FlextCliProtocolsXlsxRules,
    FlextCliProtocolsXlsxSnapshot,
    FlextCliProtocolsXlsxWorkbook,
)
from flext_cli._protocols._xlsx import (
    FlextCliProtocolsXlsxXlsxArchive,
    FlextCliProtocolsXlsxXlsxCells,
    FlextCliProtocolsXlsxXlsxLayout,
    FlextCliProtocolsXlsxXlsxRecalc,
    FlextCliProtocolsXlsxXlsxRules,
    FlextCliProtocolsXlsxXlsxSnapshot,
    FlextCliProtocolsXlsxXlsxStyleCatalog,
    FlextCliProtocolsXlsxXlsxStyleFills,
    FlextCliProtocolsXlsxXlsxStylePrimitives,
    FlextCliProtocolsXlsxXlsxStyles,
    FlextCliProtocolsXlsxXlsxTables,
    FlextCliProtocolsXlsxXlsxValidation,
    FlextCliProtocolsXlsxXlsxWorkbook,
)

if TYPE_CHECKING:
    from flext_core import p


class FlextCliProtocolsXlsx(
    FlextCliProtocolsXlsxXlsxSnapshot,
    FlextCliProtocolsXlsxXlsxRecalc,
    FlextCliProtocolsXlsxXlsxWorkbook,
    FlextCliProtocolsXlsxXlsxArchive,
    FlextCliProtocolsXlsxXlsxStyleCatalog,
    FlextCliProtocolsXlsxXlsxRules,
    FlextCliProtocolsXlsxXlsxValidation,
    FlextCliProtocolsXlsxXlsxTables,
    FlextCliProtocolsXlsxXlsxLayout,
    FlextCliProtocolsXlsxXlsxStyles,
    FlextCliProtocolsXlsxXlsxStylePrimitives,
    FlextCliProtocolsXlsxXlsxStyleFills,
    FlextCliProtocolsXlsxXlsxCells,
    FlextCliProtocolsXlsxArchive,
    FlextCliProtocolsXlsxSnapshot,
    FlextCliProtocolsXlsxWorkbook,
    FlextCliProtocolsXlsxRules,
):
    """Consumer protocols for plans, requests, results, and services."""

    # NOTE (multi-agent, mro-j2yt.1): protocol properties retain the exact
    # source model objects; no dump, mapping, or adapter DTO is introduced.

    # mro-j2yt.1 (xlsx_reference_api): public structural formatting boundary.

    @runtime_checkable
    class XlsxService(FlextCliProtocolsXlsxSnapshot.XlsxSnapshotService, Protocol):
        def xlsx_parse_range(
            self,
            request: FlextCliProtocolsXlsxXlsxCells.XlsxParseRangeRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxCells.XlsxCellRange]:
            """Parse one cell range reference from the request."""
            ...

        def xlsx_format_reference(
            self,
            request: FlextCliProtocolsXlsxXlsxCells.XlsxFormatReferenceRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxCells.XlsxReference]:
            """Format one cell range reference from the request."""
            ...

        def xlsx_render(
            self,
            request: FlextCliProtocolsXlsxXlsxWorkbook.XlsxRenderRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxWorkbook.XlsxRenderResult]:
            """Render workbook bytes according to the request plan."""
            ...

        def xlsx_inspect(
            self,
            request: FlextCliProtocolsXlsxXlsxArchive.XlsxArchiveInspectionRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxArchive.XlsxArchiveInspection]:
            """Inspect the workbook archive described by the request."""
            ...

        def xlsx_style_catalog(
            self,
            request: FlextCliProtocolsXlsxXlsxStyleCatalog.XlsxStyleCatalogRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxStyleCatalog.XlsxStyleCatalog]:
            """Extract the style catalog from the request workbook bytes."""
            ...

        def xlsx_style_template(
            self,
            request: FlextCliProtocolsXlsxXlsxStyleCatalog.XlsxStyleTemplateRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxStyleCatalog.XlsxStyleTemplateResult]:
            """Render a styled template from the request catalog."""
            ...

        def xlsx_recalc(
            self,
            request: FlextCliProtocolsXlsxXlsxRecalc.XlsxRecalcRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxRecalc.XlsxRecalcResult]:
            """Recalculate workbook bytes through the request contract."""
            ...

        def xlsx_recalc_parity(
            self,
            request: FlextCliProtocolsXlsxXlsxRecalc.XlsxRecalcParityRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxRecalc.XlsxRecalcParityReport]:
            """Validate recalculation parity for the request inputs."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsXlsx",)
