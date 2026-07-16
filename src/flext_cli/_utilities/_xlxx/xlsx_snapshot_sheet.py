"""Worksheet assembly for typed XLSX semantic snapshots."""

from __future__ import annotations

from typing import Literal

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

from flext_cli import m, p, r

from .xlsx_snapshot_structure import FlextCliUtilitiesXlsxSnapshotStructure
from .xlsx_snapshot_values import FlextCliUtilitiesXlsxSnapshotValues


class FlextCliUtilitiesXlsxSnapshotSheet(
    FlextCliUtilitiesXlsxSnapshotValues, FlextCliUtilitiesXlsxSnapshotStructure
):
    """Build one immutable worksheet snapshot from formula and value views."""

    # NOTE (multi-agent, mro-wkii.17.26): formula structure stays authoritative;
    # vendor aggregation and model validation use narrow exception boundaries.
    @staticmethod
    def _snapshot_state(
        worksheet: Worksheet,
    ) -> p.Result[Literal["visible", "hidden", "veryHidden"]]:
        if worksheet.sheet_state == "visible":
            return r[Literal["visible", "hidden", "veryHidden"]].ok("visible")
        if worksheet.sheet_state == "hidden":
            return r[Literal["visible", "hidden", "veryHidden"]].ok("hidden")
        if worksheet.sheet_state == "veryHidden":
            return r[Literal["visible", "hidden", "veryHidden"]].ok("veryHidden")
        return r[Literal["visible", "hidden", "veryHidden"]].fail(
            f"Unsupported worksheet state: {worksheet.sheet_state}"
        )

    @classmethod
    def _snapshot_sheet(
        cls, formula_sheet: Worksheet, value_sheet: Worksheet, *, position: int
    ) -> p.Result[p.Cli.XlsxSheetSnapshot]:
        formula_title = formula_sheet.title
        value_title = value_sheet.title
        if formula_title != value_title:
            return r[p.Cli.XlsxSheetSnapshot].fail(
                "Worksheet snapshot failed (ValueError): Worksheet view mismatch: "
                f"{formula_title} != {value_title}"
            )
        try:
            state, cells, tables, rows, columns = (
                cls._require_success(cls._snapshot_state(formula_sheet)),
                cls._require_success(
                    cls._snapshot_cells(
                        formula_sheet,
                        value_sheet,
                        data_only=formula_sheet is not value_sheet,
                    )
                ),
                cls._require_success(cls._snapshot_tables(formula_sheet)),
                cls._require_success(cls._snapshot_rows(formula_sheet)),
                cls._require_success(cls._snapshot_columns(formula_sheet)),
            )
            merged_ranges = tuple(
                sorted(str(item) for item in formula_sheet.merged_cells.ranges)
            )
            legacy_password_hash = formula_sheet.protection.password
        except (TypeError, ValidationError, ValueError) as exc:
            return r[p.Cli.XlsxSheetSnapshot].fail(
                f"Worksheet snapshot failed ({exc.__class__.__name__}): {exc}",
                exception=exc,
            )
        if legacy_password_hash is not None and not isinstance(
            legacy_password_hash, str
        ):
            return r[p.Cli.XlsxSheetSnapshot].fail(
                "Worksheet snapshot failed (TypeError): Worksheet legacy protection "
                "hash is not textual"
            )
        try:
            snapshot = m.Cli.XlsxSheetSnapshot(
                name=formula_title,
                position=position,
                state=state,
                max_row=formula_sheet.max_row,
                max_column=formula_sheet.max_column,
                cells=cells,
                tables=tables,
                row_dimensions=rows,
                column_dimensions=columns,
                merged_ranges=merged_ranges,
                freeze_pane=formula_sheet.freeze_panes,
                auto_filter=formula_sheet.auto_filter.ref,
                protection=(
                    m.Cli.XlsxSheetProtectionSnapshot(
                        enabled=formula_sheet.protection.sheet,
                        legacy_password_hash=legacy_password_hash,
                    )
                ),
                formula_count=sum(item.formula is not None for item in cells),
                literal_count=sum(
                    item.formula is None and item.value.kind != "blank"
                    for item in cells
                ),
                data_validation_count=len(
                    formula_sheet.data_validations.dataValidation
                ),
                conditional_format_count=sum(
                    len(formula_sheet.conditional_formatting[item])
                    for item in formula_sheet.conditional_formatting
                ),
                merge_count=len(merged_ranges),
            )
        except (TypeError, ValidationError, ValueError) as exc:
            return r[p.Cli.XlsxSheetSnapshot].fail(
                f"Worksheet snapshot failed ({exc.__class__.__name__}): {exc}",
                exception=exc,
            )
        return r[p.Cli.XlsxSheetSnapshot].ok(snapshot)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxSnapshotSheet",)
