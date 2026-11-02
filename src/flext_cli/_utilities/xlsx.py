"""Lightweight public utility boundary for generic XLSX bytes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p
from flext_cli._utilities import _xlsx


class FlextCliUtilitiesXlsx:
    """Load XLSX adapters only when their public operation executes."""

    @staticmethod
    def xlsx_render(
        request: p.Cli.XlsxRenderRequest,
    ) -> p.Result[p.Cli.XlsxRenderResult]:
        """Render a typed workbook through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxRenderResult]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxRenderer.render_workbook(request)

    @staticmethod
    def xlsx_snapshot(
        request: p.Cli.XlsxSnapshotRequest,
    ) -> p.Result[p.Cli.XlsxWorkbookSnapshot]:
        """Snapshot workbook bytes through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxWorkbookSnapshot]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxSnapshot.snapshot_workbook(request)

    @staticmethod
    def xlsx_inspect(
        request: p.Cli.XlsxArchiveInspectionRequest,
    ) -> p.Result[p.Cli.XlsxArchiveInspection]:
        """Inspect workbook bytes through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxArchiveInspection]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxArchive.inspect_archive(request)

    @staticmethod
    def xlsx_recalc(
        request: p.Cli.XlsxRecalcRequest,
    ) -> p.Result[p.Cli.XlsxRecalcResult]:
        """Recalculate workbook bytes through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxRecalcResult]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxRecalc.recalculate_workbook(request)

    @staticmethod
    def xlsx_recalc_parity(
        request: p.Cli.XlsxRecalcParityRequest,
    ) -> p.Result[p.Cli.XlsxRecalcParityReport]:
        """Prove recalculation parity through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxRecalcParityReport]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxRecalc.verify_recalculation_parity(request)

    @staticmethod
    def xlsx_defined_name_values(
        request: p.Cli.XlsxDefinedNameValuesRequest,
    ) -> p.Result[p.Cli.XlsxDefinedNameValuesResult]:
        """Resolve defined names through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxDefinedNameValuesResult]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxDefinedNameValues.resolve_defined_name_values(
            request
        )

    @staticmethod
    def xlsx_style_catalog(
        request: p.Cli.XlsxStyleCatalogRequest,
    ) -> p.Result[p.Cli.XlsxStyleCatalog]:
        """Extract styles through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxStyleCatalog]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxStyleCatalog.extract_style_catalog(request)

    @staticmethod
    def xlsx_style_template(
        request: p.Cli.XlsxStyleTemplateRequest,
    ) -> p.Result[p.Cli.XlsxStyleTemplateResult]:
        """Build a style template through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxStyleTemplateResult]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxStyleCatalog.build_style_template(request)

    @staticmethod
    def xlsx_parse_range(
        request: p.Cli.XlsxParseRangeRequest,
    ) -> p.Result[p.Cli.XlsxCellRange]:
        """Parse a cell range through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxCellRange]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxAddresses.parse_cell_range(request)

    @staticmethod
    def xlsx_format_reference(
        request: p.Cli.XlsxFormatReferenceRequest,
    ) -> p.Result[p.Cli.XlsxReference]:
        """Format a cell reference through the causal XLSX adapter boundary.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxReference]``.

        """
        return _xlsx.FlextCliUtilitiesXlsxAddresses.format_cell_reference(request)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsx",)
