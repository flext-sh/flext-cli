"""Apply typed worksheet layout plans through public openpyxl APIs.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from openpyxl.cell.cell import Cell
from openpyxl.comments import Comment
from openpyxl.worksheet.worksheet import Worksheet

from flext_cli import c, m, p, r, t
from flext_cli._utilities import FlextCliUtilitiesXlsxAddresses


class FlextCliUtilitiesXlsxLayout(FlextCliUtilitiesXlsxAddresses):
    """Apply comments, links, dimensions, grouping, views, and merges."""

    # NOTE (multi-agent, mro-j2yt.1): merge operations run last so comments
    # and hyperlinks can still target every concrete cell in the plan.
    @classmethod
    def _apply_layout(
        cls,
        worksheet: Worksheet,
        plan: m.Cli.XlsxSheetLayoutPlan,
    ) -> p.Result[bool]:
        try:
            return cls._apply_layout_unchecked(worksheet, plan)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[bool].fail(f"{c.Cli.XlsxError.RENDER_FAILED}: {detail}")

    @classmethod
    def _apply_layout_unchecked(
        cls,
        worksheet: Worksheet,
        plan: m.Cli.XlsxSheetLayoutPlan,
    ) -> p.Result[bool]:
        annotations = cls._apply_cell_annotations(worksheet, plan)
        if annotations.failure:
            return annotations
        cls._apply_dimensions_and_groups(worksheet, plan)
        if plan.freeze_pane is not None:
            worksheet.freeze_panes = cls._cell_ref(plan.freeze_pane.at)
        if plan.auto_filter is not None:
            worksheet.auto_filter.ref = cls._range_ref(plan.auto_filter.area)
        if plan.view is not None:
            worksheet.sheet_state = plan.view.visibility
            worksheet.sheet_properties.tabColor = plan.view.tab_color
        for item in plan.merges:
            worksheet.merge_cells(cls._range_ref(item.area))
        return r[bool].ok(value=True)

    @classmethod
    def _apply_cell_annotations(
        cls,
        worksheet: Worksheet,
        plan: m.Cli.XlsxSheetLayoutPlan,
    ) -> p.Result[bool]:
        """Apply comments before links, rejecting merged cells at the same step.

        Returns:
            Success or the first merged-cell annotation error.

        """
        for item in plan.comments:
            comment = Comment(item.text, item.author)
            if item.width is not None:
                comment.width = item.width
            if item.height is not None:
                comment.height = item.height
            cell = worksheet.cell(item.at.row, item.at.column)
            if not isinstance(cell, Cell):
                return r[bool].fail(
                    f"Cannot comment merged cell: row={item.at.row}, "
                    f"column={item.at.column}",
                )
            cell.comment = comment
        for item in plan.hyperlinks:
            cell = worksheet.cell(item.at.row, item.at.column)
            if not isinstance(cell, Cell):
                return r[bool].fail(
                    f"Cannot link merged cell: row={item.at.row}, "
                    f"column={item.at.column}",
                )
            if item.kind == "external":
                cell.hyperlink = item.target
            else:
                destination = cls._cell_ref(item.destination)
                sheet = cls._sheet_ref(item.destination_sheet)
                cell.hyperlink = f"#{sheet}!{destination}"
        return r[bool].ok(value=True)

    @classmethod
    def _apply_dimensions_and_groups(
        cls,
        worksheet: Worksheet,
        plan: m.Cli.XlsxSheetLayoutPlan,
    ) -> None:
        """Apply explicit dimensions before outline groups."""
        for item in plan.dimensions:
            for index in range(item.first, item.last + 1):
                if item.axis == "row":
                    dimension = worksheet.row_dimensions[index]
                    dimension.height = item.size
                else:
                    dimension = worksheet.column_dimensions[cls._column_ref(index)]
                    if item.size is not None:
                        dimension.width = item.size
                dimension.hidden = item.hidden
        for item in plan.groups:
            if item.axis == "row":
                worksheet.row_dimensions.group(
                    item.first,
                    item.last,
                    outline_level=item.outline_level,
                    hidden=item.hidden,
                )
            else:
                worksheet.column_dimensions.group(
                    cls._column_ref(item.first),
                    cls._column_ref(item.last),
                    outline_level=item.outline_level,
                    hidden=item.hidden,
                )


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesXlsxLayout",)
