"""Generic model-driven XLSX renderer.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import r
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from flext_cli import c, m, p
from flext_cli._utilities._xlsx import (
    FlextCliUtilitiesXlsxCells,
    FlextCliUtilitiesXlsxLayout,
    FlextCliUtilitiesXlsxRules,
    FlextCliUtilitiesXlsxTables,
    FlextCliUtilitiesXlsxWorkbookPlan,
)


class FlextCliUtilitiesXlsxRenderer(
    FlextCliUtilitiesXlsxRules,
    FlextCliUtilitiesXlsxWorkbookPlan,
    FlextCliUtilitiesXlsxCells,
    FlextCliUtilitiesXlsxTables,
    FlextCliUtilitiesXlsxLayout,
):
    """Render one immutable workbook plan into XLSX bytes."""

    # NOTE (multi-agent, mro-j2yt.1): Rules precedes WorkbookPlan so the shared
    # style spine linearizes Builders -> Readers -> WorkbookIo consistently.
    # NOTE (multi-agent, mro-j2yt.1): stage order is canonical and fail-loud;
    # later stages never run after an earlier mutation reports failure.
    @classmethod
    def _render_sheet(
        cls,
        workbook: Workbook,
        plan: p.Cli.XlsxSheetPlan,
        table_names: frozenset[str],
    ) -> p.Result[frozenset[str]]:
        if plan.name not in workbook.sheetnames:
            return r[frozenset[str]].fail(
                f"{c.Cli.XlsxError.SHEET_MISSING}: {plan.name}",
            )
        # mro-j47u (codex): workbook planning creates only Worksheet instances.
        worksheet = workbook[plan.name]
        cells = cls._apply_cells(
            worksheet,
            plan.cells,
            frozenset(workbook.named_styles),
        )
        if cells.failure:
            return r[frozenset[str]].from_failure(cells)
        tables = cls._apply_tables(worksheet, plan.tables, table_names)
        if tables.failure:
            return r[frozenset[str]].from_failure(tables)
        return cls._finish_sheet(worksheet, plan, tables.value)

    @classmethod
    def _finish_sheet(
        cls,
        worksheet: Worksheet,
        plan: p.Cli.XlsxSheetPlan,
        table_names: frozenset[str],
    ) -> p.Result[frozenset[str]]:
        """Apply the layout and then the rules stage of one rendered sheet.

        Returns:
            The workbook table names after this sheet, or the first stage
            failure.

        """
        layout = cls._apply_layout(worksheet, plan.layout)
        if layout.failure:
            return r[frozenset[str]].from_failure(layout)
        rules = cls._apply_rules(worksheet, plan.rules)
        if rules.failure:
            return r[frozenset[str]].from_failure(rules)
        return r[frozenset[str]].ok(table_names)

    @classmethod
    def render_workbook(
        cls,
        request: p.Cli.XlsxRenderRequest,
    ) -> p.Result[p.Cli.XlsxRenderResult]:
        """Render typed sheets, names, styles, and rules into workbook bytes.

        Returns:
            The resulting ``p.Result[p.Cli.XlsxRenderResult]``.

        """
        workbook_result = cls._workbook_for_request(request)
        if workbook_result.failure:
            return r[p.Cli.XlsxRenderResult].from_failure(workbook_result)
        workbook = workbook_result.value
        table_names: frozenset[str] = frozenset()
        for sheet in request.plan.sheets:
            rendered = cls._render_sheet(workbook, sheet, table_names)
            if rendered.failure:
                return r[p.Cli.XlsxRenderResult].from_failure(rendered)
            table_names = rendered.value
        names = cls._apply_defined_names(workbook, request.plan.defined_names)
        if names.failure:
            return r[p.Cli.XlsxRenderResult].from_failure(names)
        content = cls._serialize_workbook(workbook)
        if content.failure:
            return r[p.Cli.XlsxRenderResult].from_failure(content)
        return r[p.Cli.XlsxRenderResult].ok(
            m.Cli.XlsxRenderResult(content=content.value, plan=request.plan),
        )


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxRenderer",)
