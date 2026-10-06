# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._models import _base, _xlsx
    from flext_cli._models._defaults import FlextCliModelsDefaults
    from flext_cli._models._xlsx.xlsx_archive import FlextCliModelsXlsxArchive
    from flext_cli._models._xlsx.xlsx_cells import FlextCliModelsXlsxCells
    from flext_cli._models._xlsx.xlsx_layout import FlextCliModelsXlsxLayout
    from flext_cli._models._xlsx.xlsx_recalc import FlextCliModelsXlsxRecalc
    from flext_cli._models._xlsx.xlsx_rules import FlextCliModelsXlsxRules
    from flext_cli._models._xlsx.xlsx_snapshot import FlextCliModelsXlsxSnapshot
    from flext_cli._models._xlsx.xlsx_style_catalog import (
        FlextCliModelsXlsxStyleCatalog,
    )
    from flext_cli._models._xlsx.xlsx_style_fills import FlextCliModelsXlsxStyleFills
    from flext_cli._models._xlsx.xlsx_style_primitives import (
        FlextCliModelsXlsxStylePrimitives,
    )
    from flext_cli._models._xlsx.xlsx_styles import FlextCliModelsXlsxStyles
    from flext_cli._models._xlsx.xlsx_tables import FlextCliModelsXlsxTables
    from flext_cli._models._xlsx.xlsx_validation import FlextCliModelsXlsxValidation
    from flext_cli._models._xlsx.xlsx_workbook import FlextCliModelsXlsxWorkbook
    from flext_cli._models.atomic_state import FlextCliModelsAtomicState
    from flext_cli._models.atomic_symlink import FlextCliModelsAtomicSymlink
    from flext_cli._models.base import FlextCliModelsBase
    from flext_cli._models.config import FlextCliConfigModels
    from flext_cli._models.docx import FlextCliModelsDocx
    from flext_cli._models.docx_document import FlextCliModelsDocxDocument
    from flext_cli._models.docx_styles import FlextCliModelsDocxStyles
    from flext_cli._models.pipeline import FlextCliModelsPipeline
    from flext_cli._models.pptx import FlextCliModelsPptx
    from flext_cli._models.pptx_presentation import FlextCliModelsPptxPresentation
    from flext_cli._models.rules import FlextCliModelsRules
    from flext_cli._models.template import FlextCliModelsTemplate
    from flext_cli._models.xlsx import FlextCliModelsXlsx


__all__: tuple[str, ...] = (
    "FlextCliConfigModels",
    "FlextCliModelsAtomicState",
    "FlextCliModelsAtomicSymlink",
    "FlextCliModelsBase",
    "FlextCliModelsDefaults",
    "FlextCliModelsDocx",
    "FlextCliModelsDocxDocument",
    "FlextCliModelsDocxStyles",
    "FlextCliModelsPipeline",
    "FlextCliModelsPptx",
    "FlextCliModelsPptxPresentation",
    "FlextCliModelsRules",
    "FlextCliModelsTemplate",
    "FlextCliModelsXlsx",
    "FlextCliModelsXlsxArchive",
    "FlextCliModelsXlsxCells",
    "FlextCliModelsXlsxLayout",
    "FlextCliModelsXlsxRecalc",
    "FlextCliModelsXlsxRules",
    "FlextCliModelsXlsxSnapshot",
    "FlextCliModelsXlsxStyleCatalog",
    "FlextCliModelsXlsxStyleFills",
    "FlextCliModelsXlsxStylePrimitives",
    "FlextCliModelsXlsxStyles",
    "FlextCliModelsXlsxTables",
    "FlextCliModelsXlsxValidation",
    "FlextCliModelsXlsxWorkbook",
    "_base",
    "_xlsx",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliConfigModels": ".config",
        "FlextCliModelsAtomicState": ".atomic_state",
        "FlextCliModelsAtomicSymlink": ".atomic_symlink",
        "FlextCliModelsBase": ".base",
        "FlextCliModelsDefaults": "._defaults",
        "FlextCliModelsDocx": ".docx",
        "FlextCliModelsDocxDocument": ".docx_document",
        "FlextCliModelsDocxStyles": ".docx_styles",
        "FlextCliModelsPipeline": ".pipeline",
        "FlextCliModelsPptx": ".pptx",
        "FlextCliModelsPptxPresentation": ".pptx_presentation",
        "FlextCliModelsRules": ".rules",
        "FlextCliModelsTemplate": ".template",
        "FlextCliModelsXlsx": ".xlsx",
        "FlextCliModelsXlsxArchive": "._xlsx.xlsx_archive",
        "FlextCliModelsXlsxCells": "._xlsx.xlsx_cells",
        "FlextCliModelsXlsxLayout": "._xlsx.xlsx_layout",
        "FlextCliModelsXlsxRecalc": "._xlsx.xlsx_recalc",
        "FlextCliModelsXlsxRules": "._xlsx.xlsx_rules",
        "FlextCliModelsXlsxSnapshot": "._xlsx.xlsx_snapshot",
        "FlextCliModelsXlsxStyleCatalog": "._xlsx.xlsx_style_catalog",
        "FlextCliModelsXlsxStyleFills": "._xlsx.xlsx_style_fills",
        "FlextCliModelsXlsxStylePrimitives": "._xlsx.xlsx_style_primitives",
        "FlextCliModelsXlsxStyles": "._xlsx.xlsx_styles",
        "FlextCliModelsXlsxTables": "._xlsx.xlsx_tables",
        "FlextCliModelsXlsxValidation": "._xlsx.xlsx_validation",
        "FlextCliModelsXlsxWorkbook": "._xlsx.xlsx_workbook",
        "_base": "._base",
        "_xlsx": "._xlsx",
    }),
    public_exports=__all__,
)
