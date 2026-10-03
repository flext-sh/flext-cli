"""Private MRO composition for generic XLSX models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import t
from flext_cli._models._xlsx.xlsx_archive import FlextCliModelsXlsxArchive
from flext_cli._models._xlsx.xlsx_cells import FlextCliModelsXlsxCells
from flext_cli._models._xlsx.xlsx_layout import FlextCliModelsXlsxLayout
from flext_cli._models._xlsx.xlsx_recalc import FlextCliModelsXlsxRecalc
from flext_cli._models._xlsx.xlsx_rules import FlextCliModelsXlsxRules
from flext_cli._models._xlsx.xlsx_snapshot import FlextCliModelsXlsxSnapshot
from flext_cli._models._xlsx.xlsx_style_catalog import FlextCliModelsXlsxStyleCatalog
from flext_cli._models._xlsx.xlsx_styles import FlextCliModelsXlsxStyles
from flext_cli._models._xlsx.xlsx_tables import FlextCliModelsXlsxTables
from flext_cli._models._xlsx.xlsx_validation import FlextCliModelsXlsxValidation
from flext_cli._models._xlsx.xlsx_workbook import FlextCliModelsXlsxWorkbook


class FlextCliModelsXlsx(
    FlextCliModelsXlsxSnapshot,
    FlextCliModelsXlsxRecalc,
    FlextCliModelsXlsxWorkbook,
    FlextCliModelsXlsxArchive,
    FlextCliModelsXlsxStyleCatalog,
    FlextCliModelsXlsxRules,
    FlextCliModelsXlsxValidation,
    FlextCliModelsXlsxTables,
    FlextCliModelsXlsxLayout,
    FlextCliModelsXlsxStyles,
    FlextCliModelsXlsxCells,
):
    """Canonical private XLSX model namespace."""

    # NOTE (multi-agent, mro-j2yt.1): snapshot declarations join the existing
    # XLSX namespace without a parallel public model surface.


__all__: t.VariadicTuple[str] = ("FlextCliModelsXlsx",)
