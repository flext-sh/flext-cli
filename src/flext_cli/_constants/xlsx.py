"""Stable constants for the generic XLSX boundary."""

from __future__ import annotations

from enum import StrEnum, unique
from typing import Final


class FlextCliConstantsXlsx:
    """Protocol constants shared by XLSX adapters and consumers."""

    # NOTE (multi-agent, mro-j2yt.1): keep workbook protocol facts out of
    # consumer packages so every external XLSX dependency has one owner.
    XLSX_MIN_INDEX: Final[int] = 1
    XLSX_MAX_OUTLINE_LEVEL: Final[int] = 8
    XLSX_RANGE_BOUNDARY_SIZE: Final[int] = 4
    XLSX_INLINE_VALIDATION_FORMULA_LIMIT: Final[int] = 255
    XLSX_DEFAULT_NUMBER_FORMAT: Final[str] = "General"
    XLSX_DEFAULT_CALCULATION_MODE: Final = "auto"
    XLSX_WORKBOOK_MEMBER: Final[str] = "xl/workbook.xml"
    XLSX_STYLES_MEMBER: Final[str] = "xl/styles.xml"
    XLSX_WORKSHEET_PREFIX: Final[str] = "xl/worksheets/sheet"
    XLSX_XML_SUFFIX: Final[str] = ".xml"
    XLSX_STYLE_GROUPS_WITH_PROTECTION: Final[frozenset[str]] = frozenset((
        "cellStyleXfs",
        "cellXfs",
    ))
    XLSX_TRUE_TOKENS: Final[frozenset[str | None]] = frozenset((
        None,
        "1",
        "on",
        "true",
    ))
    XLSX_FALSE_TOKENS: Final[frozenset[str | None]] = frozenset((
        None,
        "0",
        "false",
        "off",
    ))

    @unique
    class XlsxError(StrEnum):
        """Stable failure codes returned by the XLSX service."""

        ARCHIVE_INVALID = "xlsx_archive_invalid"
        ARCHIVE_POLICY_VIOLATION = "xlsx_archive_policy_violation"
        CELL_VALUE_UNSUPPORTED = "xlsx_cell_value_unsupported"
        DUPLICATE_DEFINED_NAME = "xlsx_duplicate_defined_name"
        DUPLICATE_SHEET = "xlsx_duplicate_sheet"
        DUPLICATE_TABLE = "xlsx_duplicate_table"
        NAMED_STYLE_MISSING = "xlsx_named_style_missing"
        PLAN_INVALID = "xlsx_plan_invalid"
        RANGE_INVALID = "xlsx_range_invalid"
        RENDER_FAILED = "xlsx_render_failed"
        SERIALIZE_FAILED = "xlsx_serialize_failed"
        SHEET_MISSING = "xlsx_sheet_missing"
        WORKBOOK_LOAD_FAILED = "xlsx_workbook_load_failed"


__all__: tuple[str, ...] = ("FlextCliConstantsXlsx",)
