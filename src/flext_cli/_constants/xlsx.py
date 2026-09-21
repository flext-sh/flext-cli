"""Stable constants for the generic XLSX boundary."""

from __future__ import annotations

from enum import StrEnum, unique
from typing import ClassVar, Final


class FlextCliConstantsXlsx:
    """Protocol constants shared by XLSX adapters and consumers."""

    # NOTE (multi-agent, mro-j2yt.1): keep workbook protocol facts out of
    # consumer packages so every external XLSX dependency has one owner.
    XLSX_MIN_INDEX: ClassVar[int] = 1
    XLSX_MAX_OUTLINE_LEVEL: ClassVar[int] = 8
    XLSX_RANGE_BOUNDARY_SIZE: ClassVar[int] = 4
    XLSX_INLINE_VALIDATION_FORMULA_LIMIT: ClassVar[int] = 255
    XLSX_DEFAULT_NUMBER_FORMAT: ClassVar[str] = "General"
    XLSX_DEFAULT_CALCULATION_MODE: Final = "auto"
    XLSX_WORKBOOK_MEMBER: ClassVar[str] = "xl/workbook.xml"
    XLSX_STYLES_MEMBER: ClassVar[str] = "xl/styles.xml"
    XLSX_WORKSHEET_PREFIX: ClassVar[str] = "xl/worksheets/sheet"
    XLSX_XML_SUFFIX: ClassVar[str] = ".xml"
    XLSX_STYLE_GROUPS_WITH_PROTECTION: ClassVar[frozenset[str]] = frozenset((
        "cellStyleXfs",
        "cellXfs",
    ))
    XLSX_TRUE_TOKENS: ClassVar[frozenset[str | None]] = frozenset((
        None,
        "1",
        "on",
        "true",
    ))
    XLSX_FALSE_TOKENS: ClassVar[frozenset[str | None]] = frozenset((
        None,
        "0",
        "false",
        "off",
    ))
    XLSX_ERROR_CELL_PREFIX: ClassVar[str] = "#"
    XLSX_PACKAGE_PREFIX: ClassVar[str] = "xl/"
    XLSX_RECALC_COMMAND: ClassVar[tuple[str, ...]] = (
        "soffice",
        "--headless",
        "--convert-to",
        "xlsx",
        "--outdir",
    )
    XLSX_RECALC_SOURCE_NAME: ClassVar[str] = "source.xlsx"
    XLSX_RECALC_TEMP_PREFIX: ClassVar[str] = "flext-xlsx-recalc-"
    XLSX_RECALC_PROFILE_DIR_NAME: ClassVar[str] = "profile"
    XLSX_RECALC_USER_PROFILE_ARGUMENT_PREFIX: ClassVar[str] = "-env:UserInstallation="
    XLSX_RECALC_TIMEOUT_SECONDS: ClassVar[float] = 120.0
    XLSX_RELATIONSHIPS_ID_ATTRIBUTE: ClassVar[str] = (
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    )
    XLSX_WORKBOOK_RELS_MEMBER: ClassVar[str] = "xl/_rels/workbook.xml.rels"

    @unique
    class XlsxError(StrEnum):
        """Stable failure codes returned by the XLSX service."""

        ARCHIVE_INVALID = "xlsx_archive_invalid"
        ARCHIVE_POLICY_VIOLATION = "xlsx_archive_policy_violation"
        CELL_VALUE_UNSUPPORTED = "xlsx_cell_value_unsupported"
        DUPLICATE_DEFINED_NAME = "xlsx_duplicate_defined_name"
        DEFINED_NAME_INVALID = "xlsx_defined_name_invalid"
        DEFINED_NAME_MISSING = "xlsx_defined_name_missing"
        DUPLICATE_SHEET = "xlsx_duplicate_sheet"
        DUPLICATE_TABLE = "xlsx_duplicate_table"
        NAMED_STYLE_MISSING = "xlsx_named_style_missing"
        PARITY_FAILED = "xlsx_parity_failed"
        PLAN_INVALID = "xlsx_plan_invalid"
        RANGE_INVALID = "xlsx_range_invalid"
        RECALC_FAILED = "xlsx_recalc_failed"
        RENDER_FAILED = "xlsx_render_failed"
        SERIALIZE_FAILED = "xlsx_serialize_failed"
        SHEET_MISSING = "xlsx_sheet_missing"
        WORKBOOK_LOAD_FAILED = "xlsx_workbook_load_failed"


__all__: tuple[str, ...] = ("FlextCliConstantsXlsx",)
