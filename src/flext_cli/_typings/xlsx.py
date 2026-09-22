"""Strict scalar aliases for the generic XLSX boundary."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from io import BytesIO
from typing import Literal

from flext_core import t


class FlextCliTypesXlsx:
    """XLSX primitives that do not depend on workbook implementations."""

    # NOTE (multi-agent, mro-j2yt.1): structured workbook payloads remain
    # Pydantic models; this facet contains only scalar and stream aliases.
    type XlsxCellPrimitive = (
        str | int | float | bool | Decimal | dt.date | dt.datetime | None
    )
    type XlsxBinaryStream = BytesIO
    type XlsxMemberNames = t.VariadicTuple[str]
    type XlsxCalcMode = Literal["auto", "autoNoTable", "manual", "none"]
    type XlsxXmlTokens = frozenset[str | None]
    type XlsxComparisonOperator = Literal[
        "between",
        "equal",
        "greaterThan",
        "greaterThanOrEqual",
        "lessThan",
        "lessThanOrEqual",
        "notBetween",
        "notEqual",
    ]
    type XlsxValidationType = Literal[
        "custom", "date", "decimal", "list", "textLength", "time", "whole"
    ]
    type XlsxArchiveViolationKind = Literal[
        "defined_name",
        "duplicate_member",
        "member",
        "member_count",
        "member_prefix",
        "member_size",
        "required_member",
        "style_protection",
        "total_size",
        "worksheet_count",
        "worksheet_tag",
    ]


__all__: t.VariadicTuple[str] = ("FlextCliTypesXlsx",)
