# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import _base as _base
    from .base import FlextCliModelsBase as FlextCliModelsBase
    from .config import FlextCliConfigModels as FlextCliConfigModels
    from .docx import FlextCliModelsDocx as FlextCliModelsDocx
    from .docx_document import FlextCliModelsDocxDocument as FlextCliModelsDocxDocument
    from .docx_styles import FlextCliModelsDocxStyles as FlextCliModelsDocxStyles
    from .pipeline import FlextCliModelsPipeline as FlextCliModelsPipeline
    from .pptx import FlextCliModelsPptx as FlextCliModelsPptx
    from .pptx_presentation import (
        FlextCliModelsPptxPresentation as FlextCliModelsPptxPresentation,
    )
    from .rules import FlextCliModelsRules as FlextCliModelsRules
    from .template import FlextCliModelsTemplate as FlextCliModelsTemplate
    from .xlsx import FlextCliModelsXlsx as FlextCliModelsXlsx
    from ._xlsx.xlsx_archive import (
        FlextCliModelsXlsxArchive as FlextCliModelsXlsxArchive,
    )
    from ._xlsx.xlsx_cells import FlextCliModelsXlsxCells as FlextCliModelsXlsxCells
    from ._xlsx.xlsx_layout import FlextCliModelsXlsxLayout as FlextCliModelsXlsxLayout
    from ._xlsx.xlsx_recalc import FlextCliModelsXlsxRecalc as FlextCliModelsXlsxRecalc
    from ._xlsx.xlsx_rules import FlextCliModelsXlsxRules as FlextCliModelsXlsxRules
    from ._xlsx.xlsx_snapshot import (
        FlextCliModelsXlsxSnapshot as FlextCliModelsXlsxSnapshot,
    )
    from ._xlsx.xlsx_style_catalog import (
        FlextCliModelsXlsxStyleCatalog as FlextCliModelsXlsxStyleCatalog,
    )
    from ._xlsx.xlsx_style_fills import (
        FlextCliModelsXlsxStyleFills as FlextCliModelsXlsxStyleFills,
    )
    from ._xlsx.xlsx_style_primitives import (
        FlextCliModelsXlsxStylePrimitives as FlextCliModelsXlsxStylePrimitives,
    )
    from ._xlsx.xlsx_styles import FlextCliModelsXlsxStyles as FlextCliModelsXlsxStyles
    from ._xlsx.xlsx_tables import FlextCliModelsXlsxTables as FlextCliModelsXlsxTables
    from ._xlsx.xlsx_validation import (
        FlextCliModelsXlsxValidation as FlextCliModelsXlsxValidation,
    )
    from ._xlsx.xlsx_workbook import (
        FlextCliModelsXlsxWorkbook as FlextCliModelsXlsxWorkbook,
    )

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._base": ("_base",),
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
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextCliConfigModels",
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
)

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
