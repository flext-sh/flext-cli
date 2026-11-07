"""Paragraph, run, table, and section formatting for DOCX rendering.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, ClassVar

from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_UNDERLINE
from docx.shared import Inches, Pt, RGBColor

from flext_cli import p

if TYPE_CHECKING:
    from docx.text.font import Font
    from docx.text.paragraph import Paragraph
    from docx.text.parfmt import ParagraphFormat


class FlextCliUtilitiesDocxFormatting:
    """Apply validated paragraph, run, table, and section plans to python-docx."""

    _FONT_VARIANTS: ClassVar[tuple[str, ...]] = (
        "superscript",
        "subscript",
        "all_caps",
        "small_caps",
    )
    _FONT_FLAGS: ClassVar[tuple[str, ...]] = ("name", "bold", "italic", "strike")
    _POINT_LENGTHS: ClassVar[tuple[str, ...]] = (
        "space_before",
        "space_after",
        "first_line_indent",
        "left_indent",
        "right_indent",
    )
    _PAGINATION_FIELDS: ClassVar[tuple[str, ...]] = (
        "keep_together",
        "keep_with_next",
        "page_break_before",
        "widow_control",
    )

    _HEX_COLOR_WITH_ALPHA_LENGTH = 8

    _ALIGNMENT_MAP: ClassVar[Mapping[str, WD_ALIGN_PARAGRAPH]] = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "distribute": WD_ALIGN_PARAGRAPH.DISTRIBUTE,
    }

    _UNDERLINE_MAP: ClassVar[Mapping[str, WD_UNDERLINE | None]] = {
        "single": WD_UNDERLINE.SINGLE,
        "double": WD_UNDERLINE.DOUBLE,
        "singleAccounting": WD_UNDERLINE(9),
        "doubleAccounting": WD_UNDERLINE(11),
    }

    _HIGHLIGHT_MAP: ClassVar[Mapping[str, WD_COLOR_INDEX | None]] = {
        name: getattr(WD_COLOR_INDEX, name.upper(), None)
        for name in (
            "yellow",
            "green",
            "cyan",
            "magenta",
            "blue",
            "red",
            "darkBlue",
            "darkCyan",
            "darkGreen",
            "darkMagenta",
            "darkRed",
            "darkYellow",
            "darkGray",
            "lightGray",
            "black",
        )
    }

    @classmethod
    def _apply_paragraph(
        cls,
        container: DocumentType | p.Cli.DocxParagraphContainer,
        plan: p.Cli.DocxParagraphPlan,
        paragraph: Paragraph | None = None,
    ) -> Paragraph:
        if paragraph is None:
            paragraph = container.add_paragraph()
        if plan.style:
            paragraph.style = plan.style
        if plan.alignment:
            paragraph.alignment = cls._ALIGNMENT_MAP[plan.alignment]
        if plan.style_spec:
            cls._apply_paragraph_style(paragraph, plan.style_spec)
        for run in plan.runs:
            cls._apply_run(paragraph, run)
        return paragraph

    @classmethod
    def _apply_paragraph_style(
        cls,
        paragraph: Paragraph,
        spec: p.Cli.DocxParagraphStyleSpec,
    ) -> None:
        if spec.font:
            if not paragraph.runs:
                paragraph.add_run()
            cls._apply_font(paragraph.runs[0].font, spec.font)
        if spec.paragraph_format:
            cls._apply_paragraph_format(
                paragraph.paragraph_format,
                spec.paragraph_format,
            )

    @classmethod
    def _apply_run(cls, paragraph: Paragraph, plan: p.Cli.DocxRunPlan) -> None:
        run = paragraph.add_run(plan.text)
        if plan.style and plan.style.font:
            cls._apply_font(run.font, plan.style.font)

    @classmethod
    def _apply_font(cls, font: Font, spec: p.Cli.DocxFontSpec) -> None:
        cls._assign_present(font, spec, cls._FONT_FLAGS)
        if spec.size is not None:
            font.size = Pt(spec.size)
        if spec.underline is not None:
            font.underline = cls._UNDERLINE_MAP.get(spec.underline, WD_UNDERLINE.SINGLE)
        if spec.color is not None:
            font.color.rgb = cls._color_value(spec.color)
        if spec.highlight is not None:
            font.highlight_color = cls._HIGHLIGHT_MAP.get(spec.highlight)
        cls._apply_font_variants(font, spec)

    @classmethod
    def _apply_font_variants(
        cls,
        font: p.Cli.DocxFontVariants,
        spec: p.Cli.DocxFontSpec,
    ) -> None:
        cls._assign_present(font, spec, cls._FONT_VARIANTS)

    @classmethod
    def _apply_paragraph_format(
        cls,
        fmt: ParagraphFormat,
        spec: p.Cli.DocxParagraphFormatSpec,
    ) -> None:
        if spec.alignment is not None:
            fmt.alignment = cls._ALIGNMENT_MAP[spec.alignment]
        for name in cls._POINT_LENGTHS:
            points = getattr(spec, name)
            if points is not None:
                setattr(fmt, name, Inches(points / 72))  # approximate points
        cls._assign_present(fmt, spec, ("line_spacing",))
        cls._apply_paragraph_pagination(fmt, spec)

    @classmethod
    def _apply_paragraph_pagination(
        cls,
        fmt: p.Cli.DocxParagraphPagination,
        spec: p.Cli.DocxParagraphFormatSpec,
    ) -> None:
        cls._assign_present(fmt, spec, cls._PAGINATION_FIELDS)

    @staticmethod
    def _assign_present(
        target: object,
        spec: p.BaseModel,
        names: tuple[str, ...],
    ) -> None:
        """Copy every declared same-named spec field that is present.

        Absent (``None``) fields leave the target's own value untouched.

        """
        for name in names:
            value = getattr(spec, name)
            if value is not None:
                setattr(target, name, value)

    @classmethod
    def _color_value(cls, color: p.Cli.DocxColor) -> RGBColor:
        if color.kind == "rgb":
            value = color.value
            if len(value) == cls._HEX_COLOR_WITH_ALPHA_LENGTH:
                value = value[2:]
            return RGBColor.from_string(value)
        if color.kind == "theme":
            # python-docx does not expose theme colors directly; fall back to a
            # neutral gray so the document remains valid.
            return RGBColor(0x80, 0x80, 0x80)
        return RGBColor(0x00, 0x00, 0x00)


__all__: list[str] = ["FlextCliUtilitiesDocxFormatting"]
