"""Typed cell extraction for XLSX semantic snapshots."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from openpyxl.cell.cell import Cell, MergedCell
from pydantic import ValidationError

from flext_cli import c, m, p, r, t

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


class FlextCliUtilitiesXlsxSnapshotValues:
    """Convert vendor cell values into canonical discriminated models."""

    # NOTE (multi-agent, mro-j2yt.1): external cell primitives are validated
    # once into XlsxCellValue and vendor instances never leave this utility.
    # NOTE (multi-agent, mro-wkii.17.26): narrow exception boundaries retain
    # the exact failing vendor/model operation and never default missing data.
    @staticmethod
    def _snapshot_style_name(cell: Cell) -> str | None:
        return cell.style

    @staticmethod
    def _require_success[T](result: p.Result[T]) -> T:
        if result.failure:
            error = result.error
            if error is None:
                msg = "Failed FlextResult omitted its error"
                raise ValueError(msg)
            raise ValueError(error)
        return result.value

    @staticmethod
    def _snapshot_value(
        value: t.Cli.XlsxCellPrimitive, *, formula_view: bool
    ) -> p.Result[p.Cli.XlsxCellValue]:
        formula = (
            value
            if formula_view and isinstance(value, str) and value.startswith("=")
            else None
        )
        if formula_view and formula is None:
            return r[p.Cli.XlsxCellValue].fail(
                f"{c.Cli.XlsxError.CELL_VALUE_UNSUPPORTED}: "
                "formula cell has no formula expression"
            )
        try:
            converted: p.Cli.XlsxCellValue = (
                m.Cli.XlsxFormulaValue(value=formula)
                if formula is not None
                else m.Cli.XlsxBlankValue()
                if value is None
                else m.Cli.XlsxBooleanValue(value=value)
                if isinstance(value, bool)
                else m.Cli.XlsxIntegerValue(value=value)
                if isinstance(value, int)
                else m.Cli.XlsxDecimalValue(value=Decimal(str(value)))
                if isinstance(value, (float, Decimal))
                else m.Cli.XlsxDateTimeValue(value=value)
                if isinstance(value, dt.datetime)
                else m.Cli.XlsxDateValue(value=value)
                if isinstance(value, dt.date)
                else m.Cli.XlsxTextValue(value=value)
            )
        except (InvalidOperation, ValidationError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxCellValue].fail(
                f"{c.Cli.XlsxError.CELL_VALUE_UNSUPPORTED}: {detail}", exception=exc
            )
        return r[p.Cli.XlsxCellValue].ok(converted)

    @staticmethod
    def _has_snapshot_content(cell: Cell) -> bool:
        return (
            cell.value is not None
            or cell.has_style
            or cell.comment is not None
            or cell.hyperlink is not None
        )

    @staticmethod
    def _formula(cell: Cell) -> str | None:
        if cell.data_type != "f":
            return None
        value = cell.value
        if not isinstance(value, str) or not value.startswith("="):
            msg = (
                f"{c.Cli.XlsxError.CELL_VALUE_UNSUPPORTED}: "
                f"invalid formula at {cell.coordinate}"
            )
            raise ValueError(msg)
        return value

    @classmethod
    def _snapshot_cell(
        cls, formula_cell: Cell, value_sheet: Worksheet, *, data_only: bool
    ) -> p.Result[p.Cli.XlsxCellSnapshot]:
        try:
            formula = cls._formula(formula_cell)
            selected = (
                value_sheet.cell(formula_cell.row, formula_cell.column)
                if data_only
                else formula_cell
            )
        except (IndexError, TypeError, ValidationError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxCellSnapshot].fail(detail, exception=exc)
        if not isinstance(selected, Cell):
            return r[p.Cli.XlsxCellSnapshot].fail(
                f"Unsupported selected cell: {formula_cell.coordinate}"
            )
        selected_value = selected.value
        if selected_value is not None and not isinstance(
            selected_value, (str, int, float, bool, Decimal, dt.date, dt.datetime)
        ):
            return r[p.Cli.XlsxCellSnapshot].fail(
                f"{c.Cli.XlsxError.CELL_VALUE_UNSUPPORTED}: "
                f"{selected_value.__class__.__name__} at {formula_cell.coordinate}"
            )
        try:
            value = cls._require_success(
                cls._snapshot_value(
                    selected_value, formula_view=formula is not None and not data_only
                )
            )
            snapshot = m.Cli.XlsxCellSnapshot(
                coordinate=formula_cell.coordinate,
                position=m.Cli.XlsxCellAddress(
                    row=formula_cell.row, column=formula_cell.column
                ),
                value=value,
                formula=formula,
                style_name=cls._snapshot_style_name(formula_cell),
                style_id=formula_cell.style_id,
                number_format=formula_cell.number_format,
                locked=formula_cell.protection.locked,
                hidden=formula_cell.protection.hidden,
            )
        except (IndexError, TypeError, ValidationError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxCellSnapshot].fail(detail, exception=exc)
        return r[p.Cli.XlsxCellSnapshot].ok(snapshot)

    @classmethod
    def _snapshot_cells(
        cls, formula_sheet: Worksheet, value_sheet: Worksheet, *, data_only: bool
    ) -> p.Result[tuple[p.Cli.XlsxCellSnapshot, ...]]:
        cells: tuple[p.Cli.XlsxCellSnapshot, ...] = ()
        try:
            for row in formula_sheet.iter_rows():
                for formula_cell in row:
                    if isinstance(
                        formula_cell, MergedCell
                    ) or not cls._has_snapshot_content(formula_cell):
                        continue
                    cells = (
                        *cells,
                        cls._require_success(
                            cls._snapshot_cell(
                                formula_cell, value_sheet, data_only=data_only
                            )
                        ),
                    )
        except ValueError as exc:
            return r[tuple[p.Cli.XlsxCellSnapshot, ...]].fail(str(exc), exception=exc)
        return r[tuple[p.Cli.XlsxCellSnapshot, ...]].ok(cells)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxSnapshotValues",)
