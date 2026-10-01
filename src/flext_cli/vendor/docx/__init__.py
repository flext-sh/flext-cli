"""Thin re-export boundary for python-docx.

Import this package instead of ``docx`` directly. The public ``Document``
function is exposed here; the underlying ``Document`` class is available in
``flext_cli.vendor.docx.document`` for type annotations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_BREAK,
    WD_LINE_SPACING,
    WD_TAB_ALIGNMENT,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.oxml.xmlchemy import BaseOxmlElement
from docx.shared import Cm, Length, Pt, RGBColor
from docx.styles.style import ParagraphStyle
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run

__all__ = [
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
    "Pt",
    "RGBColor",
    "Run",
    "Table",
    "qn",
]
