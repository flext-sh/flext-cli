# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._models import _base, _xlsx
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
    from flext_cli._models.atomic_state import (
        validate_atomic_state_path,
        validate_non_reparse_state,
        validate_parent_identity,
    )
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
    "FlextCliModelsAtomicSymlink",
    "FlextCliModelsBase",
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
    "validate_atomic_state_path",
    "validate_non_reparse_state",
    "validate_parent_identity",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._base": ("_base",),
            "._xlsx": ("_xlsx",),
            "._xlsx.xlsx_archive": ("FlextCliModelsXlsxArchive",),
            "._xlsx.xlsx_cells": ("FlextCliModelsXlsxCells",),
            "._xlsx.xlsx_layout": ("FlextCliModelsXlsxLayout",),
            "._xlsx.xlsx_recalc": ("FlextCliModelsXlsxRecalc",),
            "._xlsx.xlsx_rules": ("FlextCliModelsXlsxRules",),
            "._xlsx.xlsx_snapshot": ("FlextCliModelsXlsxSnapshot",),
            "._xlsx.xlsx_style_catalog": ("FlextCliModelsXlsxStyleCatalog",),
            "._xlsx.xlsx_style_fills": ("FlextCliModelsXlsxStyleFills",),
            "._xlsx.xlsx_style_primitives": ("FlextCliModelsXlsxStylePrimitives",),
            "._xlsx.xlsx_styles": ("FlextCliModelsXlsxStyles",),
            "._xlsx.xlsx_tables": ("FlextCliModelsXlsxTables",),
            "._xlsx.xlsx_validation": ("FlextCliModelsXlsxValidation",),
            "._xlsx.xlsx_workbook": ("FlextCliModelsXlsxWorkbook",),
            ".atomic_state": (
                "validate_atomic_state_path",
                "validate_non_reparse_state",
                "validate_parent_identity",
            ),
            ".atomic_symlink": ("FlextCliModelsAtomicSymlink",),
            ".base": ("FlextCliModelsBase",),
            ".config": ("FlextCliConfigModels",),
            ".docx": ("FlextCliModelsDocx",),
            ".docx_document": ("FlextCliModelsDocxDocument",),
            ".docx_styles": ("FlextCliModelsDocxStyles",),
            ".pipeline": ("FlextCliModelsPipeline",),
            ".pptx": ("FlextCliModelsPptx",),
            ".pptx_presentation": ("FlextCliModelsPptxPresentation",),
            ".rules": ("FlextCliModelsRules",),
            ".template": ("FlextCliModelsTemplate",),
            ".xlsx": ("FlextCliModelsXlsx",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
