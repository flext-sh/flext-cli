# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_validation
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxValidation:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxValidationMessages(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def allow_blank(self) -> bool: ...
        @property
        def show_dropdown(self) -> bool: ...
        @property
        def show_input(self) -> bool: ...
        @property
        def input_title(self) -> str | None: ...
        @property
        def input_message(self) -> str | None: ...
        @property
        def show_error(self) -> bool: ...
        @property
        def error_style(self) -> Literal["stop", "warning", "information"] | None: ...
        @property
        def error_title(self) -> str | None: ...
        @property
        def error_message(self) -> str | None: ...

    @runtime_checkable
    class XlsxInlineListSource(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["values"]: ...
        @property
        def values(self) -> tuple[str, ...]: ...

    @runtime_checkable
    class XlsxFormulaListSource(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]: ...
        @property
        def expression(self) -> str: ...

    @runtime_checkable
    class XlsxUnaryComparison(Protocol):
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
        ]: ...
        @property
        def expression(self) -> str: ...

    @runtime_checkable
    class XlsxRangeComparison(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def mode(self) -> Literal["between", "not_between"]: ...
        @property
        def minimum(self) -> str: ...
        @property
        def maximum(self) -> str: ...

    @runtime_checkable
    class XlsxListValidationPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["list"]: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def source(
            self,
        ) -> Annotated[
            p.Cli.XlsxInlineListSource | p.Cli.XlsxFormulaListSource,
            m.Field(discriminator="kind"),
        ]: ...
        @property
        def messages(self) -> p.Cli.XlsxValidationMessages: ...

    @runtime_checkable
    class XlsxComparisonValidationPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(
            self,
        ) -> Literal["whole", "decimal", "date", "time", "text_length"]: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def comparison(
            self,
        ) -> Annotated[
            p.Cli.XlsxUnaryComparison | p.Cli.XlsxRangeComparison,
            m.Field(discriminator="mode"),
        ]: ...
        @property
        def messages(self) -> p.Cli.XlsxValidationMessages: ...

    @runtime_checkable
    class XlsxCustomValidationPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["custom"]: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def expression(self) -> str: ...
        @property
        def messages(self) -> p.Cli.XlsxValidationMessages: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxValidation",
]
