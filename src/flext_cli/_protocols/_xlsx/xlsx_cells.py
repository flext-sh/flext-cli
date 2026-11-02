# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_cells
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxCells:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxCellAddress(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def row(self) -> int: ...
        @property
        def column(self) -> int: ...

    @runtime_checkable
    class XlsxCellRange(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def first(self) -> p.Cli.XlsxCellAddress: ...
        @property
        def last(self) -> p.Cli.XlsxCellAddress: ...

    @runtime_checkable
    class XlsxParseRangeRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def reference(self) -> str: ...

    @runtime_checkable
    class XlsxFormatReferenceRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def sheet(self) -> str | None: ...
        @property
        def absolute(self) -> bool: ...
        @property
        def collapse_single_cell(self) -> bool: ...

    @runtime_checkable
    class XlsxReference(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def reference(self) -> str: ...

    @runtime_checkable
    class XlsxBlankValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["blank"]: ...

    @runtime_checkable
    class XlsxTextValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["text"]: ...
        @property
        def value(self) -> str: ...

    @runtime_checkable
    class XlsxIntegerValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["integer"]: ...
        @property
        def value(self) -> int: ...

    @runtime_checkable
    class XlsxDecimalValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["decimal"]: ...
        @property
        def value(self) -> Decimal: ...

    @runtime_checkable
    class XlsxBooleanValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["boolean"]: ...
        @property
        def value(self) -> bool: ...

    @runtime_checkable
    class XlsxDateValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["date"]: ...
        @property
        def value(self) -> dt.date: ...

    @runtime_checkable
    class XlsxDateTimeValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["datetime"]: ...
        @property
        def value(self) -> t.NaiveDatetime: ...

    @runtime_checkable
    class XlsxFormulaValue(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]: ...
        @property
        def value(self) -> str: ...

    @runtime_checkable
    class XlsxCellPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def at(self) -> p.Cli.XlsxCellAddress: ...
        @property
        def value(
            self,
        ) -> Annotated[
            p.Cli.XlsxBlankValue
            | p.Cli.XlsxTextValue
            | p.Cli.XlsxIntegerValue
            | p.Cli.XlsxDecimalValue
            | p.Cli.XlsxBooleanValue
            | p.Cli.XlsxDateValue
            | p.Cli.XlsxDateTimeValue
            | p.Cli.XlsxFormulaValue,
            m.Field(discriminator="kind"),
        ]: ...
        @property
        def style(self) -> str: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxCells",
]
