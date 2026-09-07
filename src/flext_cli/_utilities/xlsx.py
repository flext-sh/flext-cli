"""Lightweight public utility boundary for generic XLSX bytes."""

from __future__ import annotations

from flext_cli import m, p


class FlextCliUtilitiesXlsx:
    """Load XLSX adapters only when their public operation executes."""

    @staticmethod
    def xlsx_render(
        request: m.Cli.XlsxRenderRequest,
    ) -> p.Result[m.Cli.XlsxRenderResult]:
        """Render a typed workbook through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_renderer import FlextCliUtilitiesXlsxRenderer

        return FlextCliUtilitiesXlsxRenderer.xlsx_render(request)

    @staticmethod
    def xlsx_snapshot(
        request: m.Cli.XlsxSnapshotRequest,
    ) -> p.Result[m.Cli.XlsxWorkbookSnapshot]:
        """Snapshot workbook bytes through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot

        return FlextCliUtilitiesXlsxSnapshot.xlsx_snapshot(request)

    @staticmethod
    def xlsx_inspect(
        request: m.Cli.XlsxArchiveInspectionRequest,
    ) -> p.Result[m.Cli.XlsxArchiveInspection]:
        """Inspect workbook bytes through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_archive import FlextCliUtilitiesXlsxArchive

        return FlextCliUtilitiesXlsxArchive.xlsx_inspect(request)

    @staticmethod
    def xlsx_recalc(
        request: m.Cli.XlsxRecalcRequest,
    ) -> p.Result[m.Cli.XlsxRecalcResult]:
        """Recalculate workbook bytes through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc

        return FlextCliUtilitiesXlsxRecalc.xlsx_recalc(request)

    @staticmethod
    def xlsx_recalc_parity(
        request: m.Cli.XlsxRecalcParityRequest,
    ) -> p.Result[m.Cli.XlsxRecalcParityReport]:
        """Prove recalculation parity through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc

        return FlextCliUtilitiesXlsxRecalc.xlsx_recalc_parity(request)

    @staticmethod
    def xlsx_defined_name_values(
        request: m.Cli.XlsxDefinedNameValuesRequest,
    ) -> p.Result[m.Cli.XlsxDefinedNameValuesResult]:
        """Resolve defined names through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_defined_name_values import (
            FlextCliUtilitiesXlsxDefinedNameValues,
        )

        return FlextCliUtilitiesXlsxDefinedNameValues.xlsx_defined_name_values(request)

    @staticmethod
    def xlsx_style_catalog(
        request: m.Cli.XlsxStyleCatalogRequest,
    ) -> p.Result[m.Cli.XlsxStyleCatalog]:
        """Extract styles through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_style_catalog import FlextCliUtilitiesXlsxStyleCatalog

        return FlextCliUtilitiesXlsxStyleCatalog.xlsx_style_catalog(request)

    @staticmethod
    def xlsx_style_template(
        request: m.Cli.XlsxStyleTemplateRequest,
    ) -> p.Result[m.Cli.XlsxStyleTemplateResult]:
        """Build a style template through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_style_catalog import FlextCliUtilitiesXlsxStyleCatalog

        return FlextCliUtilitiesXlsxStyleCatalog.xlsx_style_template(request)

    @staticmethod
    def xlsx_parse_range(
        request: m.Cli.XlsxParseRangeRequest,
    ) -> p.Result[m.Cli.XlsxCellRange]:
        """Parse a cell range through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses

        return FlextCliUtilitiesXlsxAddresses.xlsx_parse_range(request)

    @staticmethod
    def xlsx_format_reference(
        request: m.Cli.XlsxFormatReferenceRequest,
    ) -> p.Result[m.Cli.XlsxReference]:
        """Format a cell reference through the causal XLSX adapter boundary."""
        from ._xlxx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses

        return FlextCliUtilitiesXlsxAddresses.xlsx_format_reference(request)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsx",)
