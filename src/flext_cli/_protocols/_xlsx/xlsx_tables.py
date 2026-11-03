# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_tables
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxCells


class FlextCliProtocolsXlsxXlsxTables:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxTablePlan(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Table name."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Concrete table range."""
            ...

        @property
        def style(self) -> str:
            """Table style."""
            ...

        @property
        def show_first_column(self) -> bool:
            """Emphasize first column."""
            ...

        @property
        def show_last_column(self) -> bool:
            """Emphasize last column."""
            ...

        @property
        def show_row_stripes(self) -> bool:
            """Show alternating row stripes."""
            ...

        @property
        def show_column_stripes(self) -> bool:
            """Show alternating column stripes."""
            ...

    @runtime_checkable
    class XlsxRangeDefinedNamePlan(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["range"]:
            """Name kind."""
            ...

        @property
        def name(self) -> str:
            """Defined name."""
            ...

        @property
        def sheet(self) -> str:
            """Referenced worksheet."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Referenced cell range."""
            ...

    @runtime_checkable
    class XlsxFormulaDefinedNamePlan(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]:
            """Name kind."""
            ...

        @property
        def name(self) -> str:
            """Defined name."""
            ...

        @property
        def expression(self) -> str:
            """Defined-name expression."""
            ...

    type XlsxDefinedNamePlan = XlsxRangeDefinedNamePlan | XlsxFormulaDefinedNamePlan


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxTables",
]
