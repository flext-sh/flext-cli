"""Table and section layout for DOCX rendering.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from docx.document import Document as DocumentType
from docx.enum.section import WD_ORIENT
from docx.shared import Inches

from flext_cli import p
from flext_cli._utilities._documents.docx_formatting import (
    FlextCliUtilitiesDocxFormatting,
)


class FlextCliUtilitiesDocxLayout(FlextCliUtilitiesDocxFormatting):
    """Apply validated table and section plans to python-docx documents."""

    _PAGE_SIZE: ClassVar[tuple[tuple[str, str], ...]] = (
        ("page_width", "width"),
        ("page_height", "height"),
    )
    _PAGE_MARGINS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("left_margin", "left_margin"),
        ("right_margin", "right_margin"),
        ("top_margin", "top_margin"),
        ("bottom_margin", "bottom_margin"),
    )

    @classmethod
    def _apply_table(cls, document: DocumentType, plan: p.Cli.DocxTablePlan) -> None:
        table = document.add_table(rows=len(plan.rows), cols=cls._table_columns(plan))
        if plan.style:
            table.style = plan.style
        for row_idx, row_plan in enumerate(plan.rows):
            for cell_idx, cell_plan in enumerate(row_plan.cells):
                cell = table.rows[row_idx].cells[cell_idx]
                for idx, paragraph in enumerate(cell_plan.paragraphs):
                    if idx == 0:
                        cell.paragraphs[0].text = ""
                        cls._apply_paragraph(cell, paragraph, cell.paragraphs[0])
                    else:
                        cls._apply_paragraph(cell, paragraph)

    @classmethod
    def _table_columns(cls, plan: p.Cli.DocxTablePlan) -> int:
        if not plan.rows:
            return 0
        return max(len(row.cells) for row in plan.rows) if plan.rows else 0

    @classmethod
    def _apply_sections(
        cls,
        document: DocumentType,
        sections: tuple[p.Cli.DocxSectionPlan, ...],
    ) -> None:
        for section_plan in sections:
            section = document.add_section()
            cls._assign_emu_lengths(section, section_plan, cls._PAGE_SIZE)
            if section_plan.orientation == "landscape":
                section.orientation = WD_ORIENT.LANDSCAPE
            cls._assign_emu_lengths(section, section_plan, cls._PAGE_MARGINS)

    @staticmethod
    def _assign_emu_lengths(
        section: object,
        plan: p.Cli.DocxSectionPlan,
        fields: tuple[tuple[str, str], ...],
    ) -> None:
        """Copy every present EMU plan length onto its section attribute."""
        for attribute, name in fields:
            emu = getattr(plan, name)
            if emu is not None:
                setattr(section, attribute, Inches(emu / 914400))  # EMU to inches


__all__: list[str] = ["FlextCliUtilitiesDocxLayout"]
