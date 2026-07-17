"""Apply positive typed protection permissions at the openpyxl edge."""

from __future__ import annotations

from openpyxl.styles import Protection

from flext_cli import c, p, r
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


class FlextCliUtilitiesXlsxProtection:
    """Translate explicit cell rules and positive worksheet permissions."""

    # mro-wkii.17.26 (xlsx-a): keep one responsibility per vendor phase.
    @staticmethod
    def _apply_cell_protection(
        worksheet: Worksheet, plan: p.Cli.XlsxSheetProtectionPlan
    ) -> None:
        for item in plan.cells:
            for row in range(item.area.first.row, item.area.last.row + 1):
                for column in range(item.area.first.column, item.area.last.column + 1):
                    worksheet.cell(row, column).protection = Protection(
                        locked=item.locked, hidden=item.hidden
                    )

    @staticmethod
    def _apply_sheet_permissions(
        worksheet: Worksheet, plan: p.Cli.XlsxSheetProtectionPlan
    ) -> None:
        permissions = plan.permissions
        protection = worksheet.protection
        protection.sheet = True
        protection.selectLockedCells = not permissions.allow_select_locked
        protection.selectUnlockedCells = not permissions.allow_select_unlocked
        protection.formatCells = not permissions.allow_format_cells
        protection.formatColumns = not permissions.allow_format_columns
        protection.formatRows = not permissions.allow_format_rows
        protection.insertColumns = not permissions.allow_insert_columns
        protection.insertRows = not permissions.allow_insert_rows
        protection.insertHyperlinks = not permissions.allow_insert_hyperlinks
        protection.deleteColumns = not permissions.allow_delete_columns
        protection.deleteRows = not permissions.allow_delete_rows
        protection.sort = not permissions.allow_sort
        protection.autoFilter = not permissions.allow_auto_filter
        protection.pivotTables = not permissions.allow_pivot_tables
        protection.objects = not permissions.allow_edit_objects
        protection.scenarios = not permissions.allow_edit_scenarios

    @staticmethod
    def _apply_protection_credential(
        worksheet: Worksheet, plan: p.Cli.XlsxSheetProtectionPlan
    ) -> None:
        credential = plan.credential
        if credential is None:
            return
        if credential.kind == "legacy_hash":
            worksheet.protection.set_password(credential.value, already_hashed=True)
        else:
            worksheet.protection.set_password(credential.value)

    # NOTE (multi-agent, mro-j2yt.1): SheetProtection booleans express denied
    # actions, so positive allow_* model flags are inverted exactly once here.
    @classmethod
    def _apply_protection(
        cls, worksheet: Worksheet, plan: p.Cli.XlsxSheetProtectionPlan | None
    ) -> p.Result[bool]:
        if plan is None:
            return r[bool].ok(True)
        if any(
            item.area.first.row > item.area.last.row
            or item.area.first.column > item.area.last.column
            for item in plan.cells
        ):
            return r[bool].fail("Cell protection range is inverted")
        try:
            cls._apply_cell_protection(worksheet, plan)
            cls._apply_sheet_permissions(worksheet, plan)
            cls._apply_protection_credential(worksheet, plan)
        except (TypeError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[bool].fail(f"{c.Cli.XlsxError.RENDER_FAILED}: {detail}")
        return r[bool].ok(True)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxProtection",)
