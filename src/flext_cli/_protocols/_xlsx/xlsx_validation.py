# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_validation
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxCells


class FlextCliProtocolsXlsxXlsxValidation:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxValidationMessages(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def allow_blank(self) -> bool:
            """Allow blank cells."""
            ...

        @property
        def show_dropdown(self) -> bool:
            """Show list selector."""
            ...

        @property
        def show_input(self) -> bool:
            """Show input guidance."""
            ...

        @property
        def input_title(self) -> str | None:
            """Input title."""
            ...

        @property
        def input_message(self) -> str | None:
            """Input message."""
            ...

        @property
        def show_error(self) -> bool:
            """Show validation error."""
            ...

        @property
        def error_style(self) -> Literal["stop", "warning", "information"] | None:
            """Error behavior."""
            ...

        @property
        def error_title(self) -> str | None:
            """Error title."""
            ...

        @property
        def error_message(self) -> str | None:
            """Error message."""
            ...

    @runtime_checkable
    class XlsxInlineListSource(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["values"]:
            """Source kind."""
            ...

        @property
        def values(self) -> tuple[str, ...]:
            """Allowed literal values."""
            ...

    @runtime_checkable
    class XlsxFormulaListSource(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]:
            """Source kind."""
            ...

        @property
        def expression(self) -> str:
            """List formula or name."""
            ...

    @runtime_checkable
    class XlsxUnaryComparison(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def mode(
            self,
        ) -> Literal[
            "equal",
            "not_equal",
            "less_than",
            "less_or_equal",
            "greater_than",
            "greater_or_equal",
        ]:
            """Unary comparison operator."""
            ...

        @property
        def expression(self) -> str:
            """Comparison operand."""
            ...

    @runtime_checkable
    class XlsxRangeComparison(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def mode(self) -> Literal["between", "not_between"]:
            """Range comparison operator."""
            ...

        @property
        def minimum(self) -> str:
            """Lower comparison operand."""
            ...

        @property
        def maximum(self) -> str:
            """Upper comparison operand."""
            ...

    @runtime_checkable
    class XlsxListValidationPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["list"]:
            """Rule kind."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Validated cell range."""
            ...

        @property
        def source(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxValidation.XlsxInlineListSource
            | FlextCliProtocolsXlsxXlsxValidation.XlsxFormulaListSource
        ):
            """Allowed-value source."""
            ...

        @property
        def messages(
            self,
        ) -> FlextCliProtocolsXlsxXlsxValidation.XlsxValidationMessages:
            """Validation UI behavior."""
            ...

    @runtime_checkable
    class XlsxComparisonValidationPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["whole", "decimal", "date", "time", "text_length"]:
            """Rule kind."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Validated cell range."""
            ...

        @property
        def comparison(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxValidation.XlsxUnaryComparison
            | FlextCliProtocolsXlsxXlsxValidation.XlsxRangeComparison
        ):
            """Typed comparison."""
            ...

        @property
        def messages(
            self,
        ) -> FlextCliProtocolsXlsxXlsxValidation.XlsxValidationMessages:
            """Validation UI behavior."""
            ...

    @runtime_checkable
    class XlsxCustomValidationPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["custom"]:
            """Rule kind."""
            ...

        @property
        def area(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellRange:
            """Validated cell range."""
            ...

        @property
        def expression(self) -> str:
            """Custom validation formula."""
            ...

        @property
        def messages(
            self,
        ) -> FlextCliProtocolsXlsxXlsxValidation.XlsxValidationMessages:
            """Validation UI behavior."""
            ...

    type XlsxListSource = XlsxInlineListSource | XlsxFormulaListSource

    type XlsxComparison = XlsxUnaryComparison | XlsxRangeComparison

    type XlsxDataValidationPlan = (
        XlsxListValidationPlan | XlsxComparisonValidationPlan | XlsxCustomValidationPlan
    )


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxValidation",
]
