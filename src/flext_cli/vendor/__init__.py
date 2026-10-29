# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.vendor package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType

from flext_core.lazy import install_lazy_exports

from flext_cli.vendor.docx import (
    WD_ALIGN_PARAGRAPH,
    WD_BREAK,
    WD_CELL_VERTICAL_ALIGNMENT,
    WD_LINE_SPACING,
    WD_TAB_ALIGNMENT,
    WD_TABLE_ALIGNMENT,
    BaseOxmlElement,
    Cm,
    Document,
    Length,
    OxmlElement,
    Paragraph,
    ParagraphStyle,
    Pt,
    RGBColor,
    Run,
    Table,
    qn,
)
from flext_cli.vendor.pptx.presentation import Presentation

__all__: tuple[str, ...] = (
    "WD_ALIGN_PARAGRAPH",
    "WD_BREAK",
    "WD_CELL_VERTICAL_ALIGNMENT",
    "WD_LINE_SPACING",
    "WD_TABLE_ALIGNMENT",
    "WD_TAB_ALIGNMENT",
    "BaseOxmlElement",
    "Cm",
    "Document",
    "Length",
    "OxmlElement",
    "Paragraph",
    "ParagraphStyle",
    "Presentation",
    "Pt",
    "RGBColor",
    "Run",
    "Table",
    "qn",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "WD_ALIGN_PARAGRAPH": ".docx",
        "WD_BREAK": ".docx",
        "WD_CELL_VERTICAL_ALIGNMENT": ".docx",
        "WD_LINE_SPACING": ".docx",
        "WD_TABLE_ALIGNMENT": ".docx",
        "WD_TAB_ALIGNMENT": ".docx",
        "BaseOxmlElement": ".docx",
        "Cm": ".docx",
        "Document": ".docx.document",
        "Length": ".docx",
        "OxmlElement": ".docx",
        "Paragraph": ".docx",
        "ParagraphStyle": ".docx",
        "Presentation": ".pptx.presentation",
        "Pt": ".docx",
        "RGBColor": ".docx",
        "Run": ".docx",
        "Table": ".docx",
        "qn": ".docx",
    }),
    public_exports=__all__,
)
