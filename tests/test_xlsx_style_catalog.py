"""Format-only XLSX template contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from io import BytesIO

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Protection

from tests import m, tm, u


class TestsFlextCliXlsxStyleCatalog:
    """Behavioral contract validated by this module."""

    @staticmethod
    def test_xlsx_style_template_deduplicates_visuals_and_discards_content() -> None:
        """Protection differences never split a visual style signature."""
        workbook = Workbook()
        worksheet = workbook.worksheets[0]
        cells = (("A1", True), ("B1", False))
        for coordinate, locked in cells:
            cell = worksheet[coordinate]
            cell.value = coordinate
            cell.font = Font(name="Aptos", size=12, bold=True)
            cell.fill = PatternFill(fill_type="solid", fgColor="FF112233")
            cell.protection = Protection(locked=locked, hidden=not locked)
        source = BytesIO()
        workbook.save(source)

        result = u.Cli.xlsx_style_template(
            m.Cli.XlsxStyleTemplateRequest(
                source=source.getvalue(),
                style_name_prefix="visual",
            ),
        )

        tm.ok(result.success)
        tm.that(result.value.style_map, len=len(cells))
        style_names = frozenset(entry.style_name for entry in result.value.style_map)
        tm.that(style_names, len=1)
        tm.ok(next(iter(style_names)).startswith("visual_"))
        template = load_workbook(BytesIO(result.value.content))
        tm.that(tuple(template.named_styles), eq=("Normal", next(iter(style_names))))
        worksheet = template.worksheets[0]
        tm.that(worksheet.max_row, eq=1)
        tm.that(worksheet.max_column, eq=1)
        tm.that(worksheet["A1"].value, eq=None)

        inspection = u.Cli.xlsx_inspect(
            m.Cli.XlsxArchiveInspectionRequest(
                source=result.value.content,
                policy=m.Cli.XlsxArchivePolicy(
                    forbidden_worksheet_tags=frozenset(("c", "f", "mergeCells")),
                    required_worksheet_count=1,
                    reject_defined_names=True,
                    reject_style_protection=True,
                ),
            ),
        )
        tm.ok(inspection.success)
        tm.ok(inspection.value.clean)
