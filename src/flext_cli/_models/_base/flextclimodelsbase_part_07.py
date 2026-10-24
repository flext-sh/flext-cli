"""CLI Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from flext_core import m, p

from flext_cli import c, t


class FlextCliModelsBasePart07:
    """Implementation part for FlextCliModelsBasePart07."""

    class ServiceOptions(m.ArbitraryTypesModel):
        """Caller-selected native collaborators shared by CLI service instances."""

        logging_options: t.Port[p.StructlogOptions] | None = m.Field(
            default=None,
            exclude=True,
            description=(
                "Optional native Core logging composition for this application."
            ),
        )

    class TypedExtract(m.BaseModel):
        """Single contract for typed value extraction (str | bool | dict)."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")
        type_kind: Annotated[t.Cli.TypeKind, m.Field(description="Requested type")]
        value: Annotated[
            t.JsonValue | None,
            m.Field(description="Value to extract and coerce"),
        ] = None
        default: Annotated[
            t.JsonValue | None,
            m.Field(description="Fallback value when extraction fails"),
        ] = None

    class JsonWriteOptions(m.BaseModel):
        """Options for JSON file write operations."""

        indent: int = m.Field(
            default=2,
            description="JSON indentation level",
            validate_default=True,
        )
        sort_keys: bool = m.Field(
            default=False,
            description="Sort JSON keys",
            validate_default=True,
        )
        ensure_ascii: bool = m.Field(
            default=False,
            description="Escape non-ASCII chars",
            validate_default=True,
        )

    class TableRenderRequest(m.Value):
        """Validated table-rendering request for the formatter boundary."""

        columns: Annotated[
            t.StrSequence,
            m.Field(description="Ordered table column labels"),
        ]
        rows: Annotated[
            t.SequenceOf[t.StrSequence],
            m.Field(description="Ordered table row values"),
        ]
        title: Annotated[str, m.Field(description="Optional table title")] = ""

    class DataReportRequest(m.Value):
        """Validated generic data-report payload shared by every CLI domain."""

        columns: Annotated[
            t.StrSequence,
            m.Field(description="Ordered report column labels"),
        ]
        rows: Annotated[
            t.SequenceOf[t.StrSequence],
            m.Field(description="Ordered report row values"),
        ]
        title: Annotated[str, m.Field(description="Optional report title")] = ""
        message: Annotated[
            str,
            m.Field(description="Trailing verdict line emitted after the table"),
        ] = ""
        table_format: Annotated[
            c.Cli.TabularFormat,
            m.Field(description="Table rendering format for the data report"),
        ] = c.Cli.TabularFormat.SIMPLE
        show_header: Annotated[
            bool,
            m.Field(description="Whether to render the header row"),
        ] = True


__all__: list[str] = ["FlextCliModelsBasePart07"]
