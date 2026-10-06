# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models. Xlsx package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
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


__all__: tuple[str, ...] = (
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
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliModelsXlsxArchive": ".xlsx_archive",
        "FlextCliModelsXlsxCells": ".xlsx_cells",
        "FlextCliModelsXlsxLayout": ".xlsx_layout",
        "FlextCliModelsXlsxRecalc": ".xlsx_recalc",
        "FlextCliModelsXlsxRules": ".xlsx_rules",
        "FlextCliModelsXlsxSnapshot": ".xlsx_snapshot",
        "FlextCliModelsXlsxStyleCatalog": ".xlsx_style_catalog",
        "FlextCliModelsXlsxStyleFills": ".xlsx_style_fills",
        "FlextCliModelsXlsxStylePrimitives": ".xlsx_style_primitives",
        "FlextCliModelsXlsxStyles": ".xlsx_styles",
        "FlextCliModelsXlsxTables": ".xlsx_tables",
        "FlextCliModelsXlsxValidation": ".xlsx_validation",
        "FlextCliModelsXlsxWorkbook": ".xlsx_workbook",
    }),
    public_exports=__all__,
)
