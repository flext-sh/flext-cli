"""Typed cell writing for the private openpyxl adapter."""

from __future__ import annotations

from openpyxl.cell.cell import Cell
from openpyxl.utils.exceptions import IllegalCharacterError
from openpyxl.worksheet.worksheet import Worksheet

from flext_cli._constants.xlsx import FlextCliConstantsXlsx
from flext_cli._models.xlsx_cells import FlextCliModelsXlsxCells
from flext_cli._typings.xlsx import FlextCliTypesXlsx
from flext_core import p, r


class FlextCliUtilitiesXlsxCells:
    """Write validated scalar/formula models without intermediate payloads."""

    # NOTE (multi-agent, mro-j2yt.1): formulas and values stay discriminated
    # models until the one external cell-value assignment below.
    @staticmethod
    def _cell_value(
        value: FlextCliModelsXlsxCells.XlsxCellValue,
    ) -> FlextCliTypesXlsx.XlsxCellPrimitive:
        if value.kind == "blank":
            return None
        return value.value

    @classmethod
    def _apply_cells(
        cls,
        worksheet: Worksheet,
        plans: tuple[FlextCliModelsXlsxCells.XlsxCellPlan, ...],
        named_styles: frozenset[str],
    ) -> p.Result[bool]:
        try:
            for plan in plans:
                if plan.style not in named_styles:
                    return r[bool].fail(
                        f"{FlextCliConstantsXlsx.XlsxError.NAMED_STYLE_MISSING}: "
                        f"{plan.style}"
                    )
                cell = worksheet.cell(row=plan.at.row, column=plan.at.column)
                if not isinstance(cell, Cell):
                    return r[bool].fail(
                        f"Cannot write merged cell: row={plan.at.row}, "
                        f"column={plan.at.column}"
                    )
                cell.value = cls._cell_value(plan.value)
                cell.style = plan.style
        except (IllegalCharacterError, TypeError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[bool].fail(
                f"{FlextCliConstantsXlsx.XlsxError.RENDER_FAILED}: {detail}"
            )
        return r[bool].ok(True)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxCells",)
