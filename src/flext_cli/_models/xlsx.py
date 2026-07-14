"""Private MRO composition for generic XLSX models."""

from __future__ import annotations

from ._xlx.xlsx_archive import FlextCliModelsXlsxArchive
from ._xlx.xlsx_cells import FlextCliModelsXlsxCells
from ._xlx.xlsx_layout import FlextCliModelsXlsxLayout
from ._xlx.xlsx_recalc import FlextCliModelsXlsxRecalc
from ._xlx.xlsx_rules import FlextCliModelsXlsxRules
from ._xlx.xlsx_snapshot import FlextCliModelsXlsxSnapshot
from ._xlx.xlsx_style_catalog import FlextCliModelsXlsxStyleCatalog
from ._xlx.xlsx_styles import FlextCliModelsXlsxStyles
from ._xlx.xlsx_tables import FlextCliModelsXlsxTables
from ._xlx.xlsx_validation import FlextCliModelsXlsxValidation
from ._xlx.xlsx_workbook import FlextCliModelsXlsxWorkbook


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


__all__: tuple[str, ...] = ("FlextCliModelsXlsx",)
