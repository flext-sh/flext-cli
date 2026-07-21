"""Typed cell writing for the private openpyxl adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openpyxl.cell.cell import Cell
from openpyxl.utils.exceptions import IllegalCharacterError

# mro-j47u (kimi): utilities consume local facades only, never private modules.
from flext_cli import c, p, r, t

from .xlsx_formula_codec import FlextCliUtilitiesXlsxFormulaCodec

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


class FlextCliUtilitiesXlsxCells:
    """Write validated scalar/formula models without intermediate payloads."""

    # NOTE (multi-agent, mro-j2yt.1): formulas and values stay discriminated
    # models until the one external cell-value assignment below; formula text
    # crosses the boundary in OOXML storage form (_xlfn. future functions).
    @staticmethod
    def _cell_value(value: p.Cli.XlsxCellValue) -> t.Cli.XlsxCellPrimitive:
        if value.kind == "blank":
            return None
        if value.kind == "formula":
            return FlextCliUtilitiesXlsxFormulaCodec.storage_formula(value.value)
        return value.value

    @classmethod
    def _apply_cells(
        cls,
        worksheet: Worksheet,
        plans: tuple[p.Cli.XlsxCellPlan, ...],
        named_styles: frozenset[str],
    ) -> p.Result[bool]:
        try:
            for plan in plans:
                if plan.style not in named_styles:
                    return r[bool].fail(
                        f"{c.Cli.XlsxError.NAMED_STYLE_MISSING}: {plan.style}"
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
            return r[bool].fail(f"{c.Cli.XlsxError.RENDER_FAILED}: {detail}")
        return r[bool].ok(True)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxCells",)
