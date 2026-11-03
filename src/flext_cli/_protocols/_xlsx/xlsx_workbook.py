# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_workbook
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import (
        FlextCliProtocolsXlsxXlsxCells,
        FlextCliProtocolsXlsxXlsxLayout,
        FlextCliProtocolsXlsxXlsxRules,
        FlextCliProtocolsXlsxXlsxStyles,
        FlextCliProtocolsXlsxXlsxTables,
    )


class FlextCliProtocolsXlsxXlsxWorkbook:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxSheetPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Worksheet name."""
            ...

        @property
        def cells(self) -> tuple[FlextCliProtocolsXlsxXlsxCells.XlsxCellPlan, ...]:
            """Concrete cell writes."""
            ...

        @property
        def tables(self) -> tuple[FlextCliProtocolsXlsxXlsxTables.XlsxTablePlan, ...]:
            """Concrete worksheet tables."""
            ...

        @property
        def layout(self) -> FlextCliProtocolsXlsxXlsxLayout.XlsxSheetLayoutPlan:
            """Worksheet layout operations."""
            ...

        @property
        def rules(self) -> FlextCliProtocolsXlsxXlsxRules.XlsxSheetRulesPlan:
            """Worksheet validation and protection operations."""
            ...

    @runtime_checkable
    class XlsxWorkbookPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def sheets(self) -> tuple[FlextCliProtocolsXlsxXlsxWorkbook.XlsxSheetPlan, ...]:
            """Exact worksheet order."""
            ...

        @property
        def defined_names(
            self,
        ) -> tuple[
            FlextCliProtocolsXlsxXlsxTables.XlsxRangeDefinedNamePlan
            | FlextCliProtocolsXlsxXlsxTables.XlsxFormulaDefinedNamePlan,
            ...,
        ]:
            """Workbook defined names."""
            ...

        @property
        def named_styles(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxStyles.XlsxNamedStyleSpec, ...]:
            """Visual styles to register."""
            ...

        @property
        def full_calculation_on_load(self) -> bool:
            """Require complete formula recalculation."""
            ...

    @runtime_checkable
    class XlsxRenderRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def template(self) -> bytes | None:
            """Formatting template bytes."""
            ...

        @property
        def plan(self) -> FlextCliProtocolsXlsxXlsxWorkbook.XlsxWorkbookPlan:
            """Validated workbook plan."""
            ...

    @runtime_checkable
    class XlsxRenderResult(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes:
            """Rendered workbook bytes."""
            ...

        @property
        def plan(self) -> FlextCliProtocolsXlsxXlsxWorkbook.XlsxWorkbookPlan:
            """Exact source plan."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxWorkbook",
]
