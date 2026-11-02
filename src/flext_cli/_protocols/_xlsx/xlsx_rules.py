# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_rules
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxRules:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxContainsTextFormatPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["contains_text"]: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def text(self) -> str: ...
        @property
        def style(self) -> str: ...
        @property
        def stop_if_true(self) -> bool: ...

    @runtime_checkable
    class XlsxCellFormatPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["cell"]: ...
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
        def style(self) -> str: ...
        @property
        def stop_if_true(self) -> bool: ...

    @runtime_checkable
    class XlsxFormulaFormatPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["formula"]: ...
        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def expressions(self) -> tuple[str, ...]: ...
        @property
        def style(self) -> str: ...
        @property
        def stop_if_true(self) -> bool: ...

    @runtime_checkable
    class XlsxCellProtectionPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def area(self) -> p.Cli.XlsxCellRange: ...
        @property
        def locked(self) -> bool: ...
        @property
        def hidden(self) -> bool: ...

    @runtime_checkable
    class XlsxPlainProtectionCredential(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["plain"]: ...
        @property
        def value(self) -> str: ...

    @runtime_checkable
    class XlsxLegacyProtectionCredential(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["legacy_hash"]: ...
        @property
        def value(self) -> str: ...

    @runtime_checkable
    class XlsxProtectionPermissions(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def allow_select_locked(self) -> bool: ...
        @property
        def allow_select_unlocked(self) -> bool: ...
        @property
        def allow_format_cells(self) -> bool: ...
        @property
        def allow_format_columns(self) -> bool: ...
        @property
        def allow_format_rows(self) -> bool: ...
        @property
        def allow_insert_columns(self) -> bool: ...
        @property
        def allow_insert_rows(self) -> bool: ...
        @property
        def allow_insert_hyperlinks(self) -> bool: ...
        @property
        def allow_delete_columns(self) -> bool: ...
        @property
        def allow_delete_rows(self) -> bool: ...
        @property
        def allow_sort(self) -> bool: ...
        @property
        def allow_auto_filter(self) -> bool: ...
        @property
        def allow_pivot_tables(self) -> bool: ...
        @property
        def allow_edit_objects(self) -> bool: ...
        @property
        def allow_edit_scenarios(self) -> bool: ...

    @runtime_checkable
    class XlsxSheetProtectionPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def credential(
            self,
        ) -> (
            Annotated[
                p.Cli.XlsxPlainProtectionCredential
                | p.Cli.XlsxLegacyProtectionCredential,
                m.Field(discriminator="kind"),
            ]
            | None
        ): ...
        @property
        def permissions(self) -> p.Cli.XlsxProtectionPermissions: ...
        @property
        def cells(self) -> tuple[p.Cli.XlsxCellProtectionPlan, ...]: ...

    @runtime_checkable
    class XlsxSheetRulesPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def validations(
            self,
        ) -> tuple[
            Annotated[
                p.Cli.XlsxListValidationPlan
                | p.Cli.XlsxComparisonValidationPlan
                | p.Cli.XlsxCustomValidationPlan,
                m.Field(discriminator="kind"),
            ],
            ...,
        ]: ...
        @property
        def conditional_formats(
            self,
        ) -> tuple[
            Annotated[
                p.Cli.XlsxContainsTextFormatPlan
                | p.Cli.XlsxCellFormatPlan
                | p.Cli.XlsxFormulaFormatPlan,
                m.Field(discriminator="kind"),
            ],
            ...,
        ]: ...
        @property
        def protection(self) -> p.Cli.XlsxSheetProtectionPlan | None: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxRules",
]
