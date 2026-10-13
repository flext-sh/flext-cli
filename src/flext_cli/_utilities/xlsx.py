"""Lightweight public utility boundary for generic XLSX bytes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m, p, t
from flext_cli._utilities._xlxx import (
    FlextCliUtilitiesXlsxAddresses,
    FlextCliUtilitiesXlsxArchive,
    FlextCliUtilitiesXlsxDefinedNameValues,
    FlextCliUtilitiesXlsxRecalc,
    FlextCliUtilitiesXlsxRenderer,
    FlextCliUtilitiesXlsxSnapshot,
    FlextCliUtilitiesXlsxStyleCatalog,
)


class FlextCliUtilitiesXlsx:
    """Load XLSX adapters only when their public operation executes."""

    @staticmethod
    def xlsx_render(
        request: m.Cli.XlsxRenderRequest,
    ) -> p.Result[m.Cli.XlsxRenderResult]:
        """Render a typed workbook through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxRenderResult]``.

        """
        return FlextCliUtilitiesXlsxRenderer.render_workbook(request)

    @staticmethod
    def xlsx_snapshot(
        request: m.Cli.XlsxSnapshotRequest,
    ) -> p.Result[m.Cli.XlsxWorkbookSnapshot]:
        """Snapshot workbook bytes through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxWorkbookSnapshot]``.

        """
        return FlextCliUtilitiesXlsxSnapshot.snapshot_workbook(request)

    @staticmethod
    def xlsx_inspect(
        request: m.Cli.XlsxArchiveInspectionRequest,
    ) -> p.Result[m.Cli.XlsxArchiveInspection]:
        """Inspect workbook bytes through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxArchiveInspection]``.

        """
        return FlextCliUtilitiesXlsxArchive.inspect_archive(request)

    @staticmethod
    def xlsx_recalc(
        request: m.Cli.XlsxRecalcRequest,
    ) -> p.Result[m.Cli.XlsxRecalcResult]:
        """Recalculate workbook bytes through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxRecalcResult]``.

        """
        return FlextCliUtilitiesXlsxRecalc.recalculate_workbook(request)

    @staticmethod
    def xlsx_recalc_parity(
        request: m.Cli.XlsxRecalcParityRequest,
    ) -> p.Result[m.Cli.XlsxRecalcParityReport]:
        """Prove recalculation parity through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxRecalcParityReport]``.

        """
        return FlextCliUtilitiesXlsxRecalc.verify_recalculation_parity(request)

    @staticmethod
    def xlsx_defined_name_values(
        request: m.Cli.XlsxDefinedNameValuesRequest,
    ) -> p.Result[m.Cli.XlsxDefinedNameValuesResult]:
        """Resolve defined names through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxDefinedNameValuesResult]``.

        """
        return FlextCliUtilitiesXlsxDefinedNameValues.resolve_defined_name_values(
            request
        )

    @staticmethod
    def xlsx_style_catalog(
        request: m.Cli.XlsxStyleCatalogRequest,
    ) -> p.Result[m.Cli.XlsxStyleCatalog]:
        """Extract styles through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxStyleCatalog]``.

        """
        return FlextCliUtilitiesXlsxStyleCatalog.extract_style_catalog(request)

    @staticmethod
    def xlsx_style_template(
        request: m.Cli.XlsxStyleTemplateRequest,
    ) -> p.Result[m.Cli.XlsxStyleTemplateResult]:
        """Build a style template through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxStyleTemplateResult]``.

        """
        return FlextCliUtilitiesXlsxStyleCatalog.build_style_template(request)

    @staticmethod
    def xlsx_parse_range(
        request: m.Cli.XlsxParseRangeRequest,
    ) -> p.Result[m.Cli.XlsxCellRange]:
        """Parse a cell range through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxCellRange]``.

        """
        return FlextCliUtilitiesXlsxAddresses.parse_cell_range(request)

    @staticmethod
    def xlsx_format_reference(
        request: m.Cli.XlsxFormatReferenceRequest,
    ) -> p.Result[m.Cli.XlsxReference]:
        """Format a cell reference through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.XlsxReference]``.

        """
        return FlextCliUtilitiesXlsxAddresses.format_cell_reference(request)


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesXlsx",)
