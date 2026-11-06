# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_rules
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import (
        FlextCliProtocolsXlsxXlsxCells,
        FlextCliProtocolsXlsxXlsxValidation,
    )


class FlextCliProtocolsXlsxXlsxRules:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxContainsTextFormatPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["contains_text"]:
            """Format kind."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Formatted range."""
            ...

        @property
        def text(self) -> str:
            """Searched text."""
            ...

        @property
        def style(self) -> str:
            """Named style."""
            ...

        @property
        def stop_if_true(self) -> bool:
            """Stop later rules."""
            ...

    @runtime_checkable
    class XlsxCellFormatPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["cell"]:
            """Format kind."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Formatted range."""
            ...

        @property
        def comparison(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxValidation.XlsxUnaryComparison
            | FlextCliProtocolsXlsxXlsxValidation.XlsxRangeComparison
        ):
            """Cell comparison."""
            ...

        @property
        def style(self) -> str:
            """Named style."""
            ...

        @property
        def stop_if_true(self) -> bool:
            """Stop later rules."""
            ...

    @runtime_checkable
    class XlsxFormulaFormatPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]:
            """Format kind."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Formatted range."""
            ...

        @property
        def expressions(self) -> tuple[str, ...]:
            """Conditional formulas."""
            ...

        @property
        def style(self) -> str:
            """Named style."""
            ...

        @property
        def stop_if_true(self) -> bool:
            """Stop later rules."""
            ...

    @runtime_checkable
    class XlsxCellProtectionPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Protected cell range."""
            ...

        @property
        def locked(self) -> bool:
            """Locked state."""
            ...

        @property
        def hidden(self) -> bool:
            """Formula-hidden state."""
            ...

    @runtime_checkable
    class XlsxPlainProtectionCredential(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["plain"]:
            """Secret kind."""
            ...

        @property
        def value(self) -> str:
            """Resolved secret."""
            ...

    @runtime_checkable
    class XlsxLegacyProtectionCredential(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["legacy_hash"]:
            """Secret kind."""
            ...

        @property
        def value(self) -> str:
            """Legacy worksheet hash."""
            ...

    @runtime_checkable
    class XlsxProtectionPermissions(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def allow_select_locked(self) -> bool:
            """Allow selecting locked cells."""
            ...

        @property
        def allow_select_unlocked(self) -> bool:
            """Allow selecting unlocked cells."""
            ...

        @property
        def allow_format_cells(self) -> bool:
            """Allow formatting cells."""
            ...

        @property
        def allow_format_columns(self) -> bool:
            """Allow formatting columns."""
            ...

        @property
        def allow_format_rows(self) -> bool:
            """Allow formatting rows."""
            ...

        @property
        def allow_insert_columns(self) -> bool:
            """Allow inserting columns."""
            ...

        @property
        def allow_insert_rows(self) -> bool:
            """Allow inserting rows."""
            ...

        @property
        def allow_insert_hyperlinks(self) -> bool:
            """Allow inserting hyperlinks."""
            ...

        @property
        def allow_delete_columns(self) -> bool:
            """Allow deleting columns."""
            ...

        @property
        def allow_delete_rows(self) -> bool:
            """Allow deleting rows."""
            ...

        @property
        def allow_sort(self) -> bool:
            """Allow sorting."""
            ...

        @property
        def allow_auto_filter(self) -> bool:
            """Allow filtering."""
            ...

        @property
        def allow_pivot_tables(self) -> bool:
            """Allow pivot tables."""
            ...

        @property
        def allow_edit_objects(self) -> bool:
            """Allow editing objects."""
            ...

        @property
        def allow_edit_scenarios(self) -> bool:
            """Allow editing scenarios."""
            ...

    @runtime_checkable
    class XlsxSheetProtectionPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def credential(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxRules.XlsxPlainProtectionCredential
            | FlextCliProtocolsXlsxXlsxRules.XlsxLegacyProtectionCredential
            | None
        ):
            """Optional resolved protection credential."""
            ...

        @property
        def permissions(
            self,
        ) -> FlextCliProtocolsXlsxXlsxRules.XlsxProtectionPermissions:
            """Allowed worksheet operations."""
            ...

        @property
        def cells(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxRules.XlsxCellProtectionPlan, ...]:
            """Explicit cell protection."""
            ...

    @runtime_checkable
    class XlsxSheetRulesPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def validations(
            self,
        ) -> tuple[
            FlextCliProtocolsXlsxXlsxValidation.XlsxListValidationPlan
            | FlextCliProtocolsXlsxXlsxValidation.XlsxComparisonValidationPlan
            | FlextCliProtocolsXlsxXlsxValidation.XlsxCustomValidationPlan,
            ...,
        ]:
            """Data validations."""
            ...

        @property
        def conditional_formats(
            self,
        ) -> tuple[
            FlextCliProtocolsXlsxXlsxRules.XlsxContainsTextFormatPlan
            | FlextCliProtocolsXlsxXlsxRules.XlsxCellFormatPlan
            | FlextCliProtocolsXlsxXlsxRules.XlsxFormulaFormatPlan,
            ...,
        ]:
            """Conditional formats."""
            ...

        @property
        def protection(
            self,
        ) -> FlextCliProtocolsXlsxXlsxRules.XlsxSheetProtectionPlan | None:
            """Optional worksheet protection."""
            ...

    type XlsxConditionalFormatPlan = (
        XlsxContainsTextFormatPlan | XlsxCellFormatPlan | XlsxFormulaFormatPlan
    )

    type XlsxProtectionCredential = (
        XlsxPlainProtectionCredential | XlsxLegacyProtectionCredential
    )


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxRules",
]
