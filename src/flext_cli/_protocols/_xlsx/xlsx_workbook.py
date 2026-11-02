# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_workbook
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxWorkbook:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxSheetPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def cells(self) -> tuple[p.Cli.XlsxCellPlan, ...]: ...
        @property
        def tables(self) -> tuple[p.Cli.XlsxTablePlan, ...]: ...
        @property
        def layout(self) -> p.Cli.XlsxSheetLayoutPlan: ...
        @property
        def rules(self) -> p.Cli.XlsxSheetRulesPlan: ...

    @runtime_checkable
    class XlsxWorkbookPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def sheets(self) -> tuple[p.Cli.XlsxSheetPlan, ...]: ...
        @property
        def defined_names(
            self,
        ) -> tuple[
            Annotated[
                p.Cli.XlsxRangeDefinedNamePlan | p.Cli.XlsxFormulaDefinedNamePlan,
                m.Field(discriminator="kind"),
            ],
            ...,
        ]: ...
        @property
        def named_styles(self) -> tuple[p.Cli.XlsxNamedStyleSpec, ...]: ...
        @property
        def full_calculation_on_load(self) -> bool: ...

    @runtime_checkable
    class XlsxRenderRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def template(self) -> bytes | None: ...
        @property
        def plan(self) -> p.Cli.XlsxWorkbookPlan: ...

    @runtime_checkable
    class XlsxRenderResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes: ...
        @property
        def plan(self) -> p.Cli.XlsxWorkbookPlan: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxWorkbook",
]
