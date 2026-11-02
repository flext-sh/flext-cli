# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_tables
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxTables:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxTablePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def style(self) -> str: ...
        @property
        def show_first_column(self) -> bool: ...
        @property
        def show_last_column(self) -> bool: ...
        @property
        def show_row_stripes(self) -> bool: ...
        @property
        def show_column_stripes(self) -> bool: ...

    @runtime_checkable
    class XlsxRangeDefinedNamePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["range"]: ...
        @property
        def name(self) -> str: ...
        @property
        def sheet(self) -> str: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...

    @runtime_checkable
    class XlsxFormulaDefinedNamePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]: ...
        @property
        def name(self) -> str: ...
        @property
        def expression(self) -> str: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxTables",
]
