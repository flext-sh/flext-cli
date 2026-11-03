# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_cells
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli import t

if TYPE_CHECKING:
    pass


class FlextCliProtocolsXlsxXlsxCells:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxCellAddress(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def row(self) -> int:
            """One-based row index."""
            ...

        @property
        def column(self) -> int:
            """One-based column index."""
            ...

    @runtime_checkable
    class XlsxCellRange(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def first(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Top-left range address."""
            ...

        @property
        def last(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Bottom-right range address."""
            ...

    @runtime_checkable
    class XlsxParseRangeRequest(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def reference(self) -> str:
            """Concrete A1 cell or range reference."""
            ...

    @runtime_checkable
    class XlsxFormatReferenceRequest(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Validated cell range to format."""
            ...

        @property
        def sheet(self) -> str | None:
            """Optional worksheet qualifier."""
            ...

        @property
        def absolute(self) -> bool:
            """Render absolute row and column markers."""
            ...

        @property
        def collapse_single_cell(self) -> bool:
            """Render equal bounds as one cell instead of a range."""
            ...

    @runtime_checkable
    class XlsxReference(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def reference(self) -> str:
            """Formatted Excel reference."""
            ...

    @runtime_checkable
    class XlsxBlankValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["blank"]:
            """Value kind."""
            ...

    @runtime_checkable
    class XlsxTextValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["text"]:
            """Value kind."""
            ...

        @property
        def value(self) -> str:
            """Cell text."""
            ...

    @runtime_checkable
    class XlsxIntegerValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["integer"]:
            """Value kind."""
            ...

        @property
        def value(self) -> int:
            """Cell integer."""
            ...

    @runtime_checkable
    class XlsxDecimalValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["decimal"]:
            """Value kind."""
            ...

        @property
        def value(self) -> Decimal:
            """Cell decimal value."""
            ...

    @runtime_checkable
    class XlsxBooleanValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["boolean"]:
            """Value kind."""
            ...

        @property
        def value(self) -> bool:
            """Cell boolean."""
            ...

    @runtime_checkable
    class XlsxDateValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["date"]:
            """Value kind."""
            ...

        @property
        def value(self) -> dt.date:
            """Cell calendar date."""
            ...

    @runtime_checkable
    class XlsxDateTimeValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["datetime"]:
            """Value kind."""
            ...

        @property
        def value(self) -> t.NaiveDatetime:
            """Timezone-naive cell date and time."""
            ...

    @runtime_checkable
    class XlsxFormulaValue(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]:
            """Value kind."""
            ...

        @property
        def value(self) -> str:
            """Excel formula."""
            ...

    @runtime_checkable
    class XlsxCellPlan(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def at(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """Destination address."""
            ...

        @property
        def value(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxCells.XlsxBlankValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxTextValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxIntegerValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDecimalValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxBooleanValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDateValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDateTimeValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxFormulaValue
        ):
            """Typed destination value."""
            ...

        @property
        def style(self) -> str:
            """Named visual style."""
            ...

    type XlsxCellValue = (
        XlsxBlankValue
        | XlsxTextValue
        | XlsxIntegerValue
        | XlsxDecimalValue
        | XlsxBooleanValue
        | XlsxDateValue
        | XlsxDateTimeValue
        | XlsxFormulaValue
    )


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxCells",
]
