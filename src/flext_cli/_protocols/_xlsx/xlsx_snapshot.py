# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_snapshot
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import m

    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxSnapshot:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxSnapshotRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...
        @property
        def data_only(self) -> bool: ...

    @runtime_checkable
    class XlsxCellSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def coordinate(self) -> str: ...
        @property
        def position(self) -> p.Cli.XlsxCellAddress: ...
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
        def formula(self) -> str | None: ...
        @property
        def style_name(self) -> str | None: ...
        @property
        def style_id(self) -> int: ...
        @property
        def number_format(self) -> str: ...
        @property
        def locked(self) -> bool: ...
        @property
        def hidden(self) -> bool: ...

    @runtime_checkable
    class XlsxTableSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def reference(self) -> str: ...
        @property
        def style_name(self) -> str | None: ...

    @runtime_checkable
    class XlsxDefinedNameSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def expression(self) -> str: ...
        @property
        def kind(self) -> str: ...
        @property
        def sheet_position(self) -> int | None: ...
        @property
        def hidden(self) -> bool | None: ...

    @runtime_checkable
    class XlsxDefinedNameValuesRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...
        @property
        def name(self) -> str: ...

    @runtime_checkable
    class XlsxDefinedNameCell(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def sheet(self) -> str: ...
        @property
        def coordinate(self) -> str: ...
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

    @runtime_checkable
    class XlsxDefinedNameValuesResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def cells(self) -> tuple[p.Cli.XlsxDefinedNameCell, ...]: ...

    @runtime_checkable
    class XlsxRowDimensionSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def position(self) -> int: ...
        @property
        def size(self) -> float | None: ...
        @property
        def hidden(self) -> bool: ...
        @property
        def outline_level(self) -> int | None: ...

    @runtime_checkable
    class XlsxColumnDimensionSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def first(self) -> int: ...
        @property
        def last(self) -> int: ...
        @property
        def size(self) -> float | None: ...
        @property
        def hidden(self) -> bool: ...
        @property
        def outline_level(self) -> int | None: ...

    @runtime_checkable
    class XlsxSheetProtectionSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def enabled(self) -> bool: ...
        @property
        def legacy_password_hash(self) -> str | None: ...

    @runtime_checkable
    class XlsxSheetSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def position(self) -> int: ...
        @property
        def state(self) -> Literal["visible", "hidden", "veryHidden"]: ...
        @property
        def max_row(self) -> int: ...
        @property
        def max_column(self) -> int: ...
        @property
        def cells(self) -> tuple[p.Cli.XlsxCellSnapshot, ...]: ...
        @property
        def tables(self) -> tuple[p.Cli.XlsxTableSnapshot, ...]: ...
        @property
        def row_dimensions(self) -> tuple[p.Cli.XlsxRowDimensionSnapshot, ...]: ...
        @property
        def column_dimensions(
            self,
        ) -> tuple[p.Cli.XlsxColumnDimensionSnapshot, ...]: ...
        @property
        def merged_ranges(self) -> tuple[str, ...]: ...
        @property
        def freeze_pane(self) -> str | None: ...
        @property
        def auto_filter(self) -> str | None: ...
        @property
        def protection(self) -> p.Cli.XlsxSheetProtectionSnapshot: ...
        @property
        def formula_count(self) -> int: ...
        @property
        def literal_count(self) -> int: ...
        @property
        def data_validation_count(self) -> int: ...
        @property
        def conditional_format_count(self) -> int: ...
        @property
        def merge_count(self) -> int: ...

    @runtime_checkable
    class XlsxWorkbookSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def data_only(self) -> bool: ...
        @property
        def sheets(self) -> tuple[p.Cli.XlsxSheetSnapshot, ...]: ...
        @property
        def defined_names(self) -> tuple[p.Cli.XlsxDefinedNameSnapshot, ...]: ...
        @property
        def named_styles(self) -> tuple[str, ...]: ...
        @property
        def formula_count(self) -> int: ...
        @property
        def literal_count(self) -> int: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxSnapshot",
]
