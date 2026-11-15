# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols. Xlsx package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx.xlsx_archive import FlextCliProtocolsXlsxXlsxArchive
    from flext_cli._protocols._xlsx.xlsx_cells import FlextCliProtocolsXlsxXlsxCells
    from flext_cli._protocols._xlsx.xlsx_layout import FlextCliProtocolsXlsxXlsxLayout
    from flext_cli._protocols._xlsx.xlsx_recalc import FlextCliProtocolsXlsxXlsxRecalc
    from flext_cli._protocols._xlsx.xlsx_rules import FlextCliProtocolsXlsxXlsxRules
    from flext_cli._protocols._xlsx.xlsx_snapshot import (
        FlextCliProtocolsXlsxXlsxSnapshot,
    )
    from flext_cli._protocols._xlsx.xlsx_style_catalog import (
        FlextCliProtocolsXlsxXlsxStyleCatalog,
    )
    from flext_cli._protocols._xlsx.xlsx_style_fills import (
        FlextCliProtocolsXlsxXlsxStyleFills,
    )
    from flext_cli._protocols._xlsx.xlsx_style_primitives import (
        FlextCliProtocolsXlsxXlsxStylePrimitives,
    )
    from flext_cli._protocols._xlsx.xlsx_styles import FlextCliProtocolsXlsxXlsxStyles
    from flext_cli._protocols._xlsx.xlsx_tables import FlextCliProtocolsXlsxXlsxTables
    from flext_cli._protocols._xlsx.xlsx_validation import (
        FlextCliProtocolsXlsxXlsxValidation,
    )
    from flext_cli._protocols._xlsx.xlsx_workbook import (
        FlextCliProtocolsXlsxXlsxWorkbook,
    )


__all__: tuple[str, ...] = (
    "FlextCliProtocolsXlsxXlsxArchive",
    "FlextCliProtocolsXlsxXlsxCells",
    "FlextCliProtocolsXlsxXlsxLayout",
    "FlextCliProtocolsXlsxXlsxRecalc",
    "FlextCliProtocolsXlsxXlsxRules",
    "FlextCliProtocolsXlsxXlsxSnapshot",
    "FlextCliProtocolsXlsxXlsxStyleCatalog",
    "FlextCliProtocolsXlsxXlsxStyleFills",
    "FlextCliProtocolsXlsxXlsxStylePrimitives",
    "FlextCliProtocolsXlsxXlsxStyles",
    "FlextCliProtocolsXlsxXlsxTables",
    "FlextCliProtocolsXlsxXlsxValidation",
    "FlextCliProtocolsXlsxXlsxWorkbook",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliProtocolsXlsxXlsxArchive": ".xlsx_archive",
        "FlextCliProtocolsXlsxXlsxCells": ".xlsx_cells",
        "FlextCliProtocolsXlsxXlsxLayout": ".xlsx_layout",
        "FlextCliProtocolsXlsxXlsxRecalc": ".xlsx_recalc",
        "FlextCliProtocolsXlsxXlsxRules": ".xlsx_rules",
        "FlextCliProtocolsXlsxXlsxSnapshot": ".xlsx_snapshot",
        "FlextCliProtocolsXlsxXlsxStyleCatalog": ".xlsx_style_catalog",
        "FlextCliProtocolsXlsxXlsxStyleFills": ".xlsx_style_fills",
        "FlextCliProtocolsXlsxXlsxStylePrimitives": ".xlsx_style_primitives",
        "FlextCliProtocolsXlsxXlsxStyles": ".xlsx_styles",
        "FlextCliProtocolsXlsxXlsxTables": ".xlsx_tables",
        "FlextCliProtocolsXlsxXlsxValidation": ".xlsx_validation",
        "FlextCliProtocolsXlsxXlsxWorkbook": ".xlsx_workbook",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliProtocolsXlsxXlsxArchive": (
            "XlsxArchivePolicy",
            "XlsxArchiveViolation",
            "XlsxArchiveInventory",
            "XlsxArchiveInspection",
            "XlsxArchiveInspectionRequest",
        ),
        "FlextCliProtocolsXlsxXlsxCells": (
            "XlsxCellAddress",
            "XlsxCellRange",
            "XlsxParseRangeRequest",
            "XlsxFormatReferenceRequest",
            "XlsxReference",
            "XlsxBlankValue",
            "XlsxTextValue",
            "XlsxIntegerValue",
            "XlsxDecimalValue",
            "XlsxBooleanValue",
            "XlsxDateValue",
            "XlsxDateTimeValue",
            "XlsxFormulaValue",
            "XlsxCellPlan",
            "XlsxCellValue",
        ),
        "FlextCliProtocolsXlsxXlsxLayout": (
            "XlsxMergePlan",
            "XlsxCommentPlan",
            "XlsxExternalHyperlinkPlan",
            "XlsxNavigationHyperlinkPlan",
            "XlsxDimensionPlan",
            "XlsxGroupPlan",
            "XlsxFreezePanePlan",
            "XlsxAutoFilterPlan",
            "XlsxViewPlan",
            "XlsxSheetLayoutPlan",
            "XlsxHyperlinkPlan",
        ),
        "FlextCliProtocolsXlsxXlsxRecalc": (
            "XlsxRecalcRequest",
            "XlsxRecalcResult",
            "XlsxRecalcParityRequest",
            "XlsxRecalcParityReport",
        ),
        "FlextCliProtocolsXlsxXlsxRules": (
            "XlsxContainsTextFormatPlan",
            "XlsxCellFormatPlan",
            "XlsxFormulaFormatPlan",
            "XlsxCellProtectionPlan",
            "XlsxPlainProtectionCredential",
            "XlsxLegacyProtectionCredential",
            "XlsxProtectionPermissions",
            "XlsxSheetProtectionPlan",
            "XlsxSheetRulesPlan",
            "XlsxConditionalFormatPlan",
            "XlsxProtectionCredential",
        ),
        "FlextCliProtocolsXlsxXlsxSnapshot": (
            "XlsxSnapshotRequest",
            "XlsxCellSnapshot",
            "XlsxTableSnapshot",
            "XlsxDefinedNameSnapshot",
            "XlsxDefinedNameValuesRequest",
            "XlsxDefinedNameCell",
            "XlsxDefinedNameValuesResult",
            "XlsxRowDimensionSnapshot",
            "XlsxColumnDimensionSnapshot",
            "XlsxSheetProtectionSnapshot",
            "XlsxSheetSnapshot",
            "XlsxWorkbookSnapshot",
        ),
        "FlextCliProtocolsXlsxXlsxStyleCatalog": (
            "XlsxStyleMapEntry",
            "XlsxSourceVisualStyle",
            "XlsxStyleCatalog",
            "XlsxStyleCatalogRequest",
            "XlsxStyleTemplateRequest",
            "XlsxStyleTemplateResult",
        ),
        "FlextCliProtocolsXlsxXlsxStyleFills": (
            "XlsxPatternFillSpec",
            "XlsxGradientStop",
            "XlsxGradientFillSpec",
            "XlsxFillSpec",
        ),
        "FlextCliProtocolsXlsxXlsxStylePrimitives": (
            "XlsxRgbColor",
            "XlsxIndexedColor",
            "XlsxThemeColor",
            "XlsxAutomaticColor",
            "XlsxFontSpec",
            "XlsxColor",
        ),
        "FlextCliProtocolsXlsxXlsxStyles": (
            "XlsxBorderSideSpec",
            "XlsxBorderSpec",
            "XlsxAlignmentSpec",
            "XlsxVisualStyleSpec",
            "XlsxNamedStyleSpec",
        ),
        "FlextCliProtocolsXlsxXlsxTables": (
            "XlsxTablePlan",
            "XlsxRangeDefinedNamePlan",
            "XlsxFormulaDefinedNamePlan",
            "XlsxDefinedNamePlan",
        ),
        "FlextCliProtocolsXlsxXlsxValidation": (
            "XlsxValidationMessages",
            "XlsxInlineListSource",
            "XlsxFormulaListSource",
            "XlsxUnaryComparison",
            "XlsxRangeComparison",
            "XlsxListValidationPlan",
            "XlsxComparisonValidationPlan",
            "XlsxCustomValidationPlan",
            "XlsxListSource",
            "XlsxComparison",
            "XlsxDataValidationPlan",
        ),
        "FlextCliProtocolsXlsxXlsxWorkbook": (
            "XlsxSheetPlan",
            "XlsxWorkbookPlan",
            "XlsxRenderRequest",
            "XlsxRenderResult",
        ),
    },
)
