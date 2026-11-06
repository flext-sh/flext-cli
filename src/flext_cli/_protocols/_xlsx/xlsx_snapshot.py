# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_snapshot
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxCells


class FlextCliProtocolsXlsxXlsxSnapshot:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxSnapshotRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Source workbook bytes."""
            ...

        @property
        def data_only(self) -> bool:
            """Read cached values instead of formulas."""
            ...

    @runtime_checkable
    class XlsxCellSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def coordinate(self) -> str:
            """A1 cell coordinate."""
            ...

        @property
        def position(self) -> FlextCliProtocolsXlsxXlsxCells.XlsxCellAddress:
            """One-based row and column position."""
            ...

        @property
        def value(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxCells.XlsxBlankValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxTextValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxIntegerValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDecimalValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxBooleanValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDateValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDateTimeValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxFormulaValue
        ):
            """Typed value from the selected workbook view."""
            ...

        @property
        def formula(self) -> str | None:
            """Original formula when this is a formula cell."""
            ...

        @property
        def style_name(self) -> str | None:
            """Applied named style."""
            ...

        @property
        def style_id(self) -> int:
            """Source workbook style identifier."""
            ...

        @property
        def number_format(self) -> str:
            """Applied number format."""
            ...

        @property
        def locked(self) -> bool:
            """Cell protection locked state."""
            ...

        @property
        def hidden(self) -> bool:
            """Cell protection hidden state."""
            ...

    @runtime_checkable
    class XlsxTableSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Table name."""
            ...

        @property
        def reference(self) -> str:
            """Table range reference."""
            ...

        @property
        def style_name(self) -> str | None:
            """Optional table style name."""
            ...

    @runtime_checkable
    class XlsxDefinedNameSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Defined name."""
            ...

        @property
        def expression(self) -> str:
            """Defined-name expression."""
            ...

        @property
        def kind(self) -> str:
            """Defined-name value kind."""
            ...

        @property
        def sheet_position(self) -> int | None:
            """Zero-based local sheet position."""
            ...

        @property
        def hidden(self) -> bool | None:
            """Defined-name hidden state when declared."""
            ...

    @runtime_checkable
    class XlsxDefinedNameValuesRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Source workbook bytes."""
            ...

        @property
        def name(self) -> str:
            """Defined name to resolve."""
            ...

    @runtime_checkable
    class XlsxDefinedNameCell(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def sheet(self) -> str:
            """Owning worksheet name."""
            ...

        @property
        def coordinate(self) -> str:
            """A1 cell coordinate."""
            ...

        @property
        def value(
            self,
        ) -> (
            FlextCliProtocolsXlsxXlsxCells.XlsxBlankValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxTextValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxIntegerValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDecimalValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxBooleanValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDateValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxDateTimeValue
            | FlextCliProtocolsXlsxXlsxCells.XlsxFormulaValue
        ):
            """Typed cached value from the data-only workbook view."""
            ...

    @runtime_checkable
    class XlsxDefinedNameValuesResult(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Resolved defined name."""
            ...

        @property
        def cells(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxDefinedNameCell, ...]:
            """Ordered cached cell values for the defined-name extent."""
            ...

    @runtime_checkable
    class XlsxRowDimensionSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def position(self) -> int:
            """One-based row index."""
            ...

        @property
        def size(self) -> float | None:
            """Explicit row height."""
            ...

        @property
        def hidden(self) -> bool:
            """Hidden row state."""
            ...

        @property
        def outline_level(self) -> int | None:
            """Row outline level."""
            ...

    @runtime_checkable
    class XlsxColumnDimensionSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Column dimension key."""
            ...

        @property
        def first(self) -> int:
            """First column index."""
            ...

        @property
        def last(self) -> int:
            """Last column index."""
            ...

        @property
        def size(self) -> float | None:
            """Explicit column width."""
            ...

        @property
        def hidden(self) -> bool:
            """Hidden column state."""
            ...

        @property
        def outline_level(self) -> int | None:
            """Column outline level."""
            ...

    @runtime_checkable
    class XlsxSheetProtectionSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def enabled(self) -> bool:
            """Whether worksheet protection is active."""
            ...

        @property
        def legacy_password_hash(self) -> str | None:
            """Stored legacy protection hash."""
            ...

    @runtime_checkable
    class XlsxSheetSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Worksheet name."""
            ...

        @property
        def position(self) -> int:
            """One-based worksheet position."""
            ...

        @property
        def state(self) -> Literal["visible", "hidden", "veryHidden"]:
            """Worksheet visibility state."""
            ...

        @property
        def max_row(self) -> int:
            """Maximum occupied row."""
            ...

        @property
        def max_column(self) -> int:
            """Maximum occupied column."""
            ...

        @property
        def cells(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxCellSnapshot, ...]:
            """Ordered semantic cells."""
            ...

        @property
        def tables(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxTableSnapshot, ...]:
            """Ordered worksheet tables."""
            ...

        @property
        def row_dimensions(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxRowDimensionSnapshot, ...]:
            """Explicit row dimensions."""
            ...

        @property
        def column_dimensions(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxColumnDimensionSnapshot, ...]:
            """Explicit column dimensions."""
            ...

        @property
        def merged_ranges(self) -> tuple[str, ...]:
            """Ordered merged ranges."""
            ...

        @property
        def freeze_pane(self) -> str | None:
            """Optional frozen-pane coordinate."""
            ...

        @property
        def auto_filter(self) -> str | None:
            """Optional auto-filter range."""
            ...

        @property
        def protection(
            self,
        ) -> FlextCliProtocolsXlsxXlsxSnapshot.XlsxSheetProtectionSnapshot:
            """Vendor-independent worksheet protection evidence."""
            ...

        @property
        def formula_count(self) -> int:
            """Formula cell count."""
            ...

        @property
        def literal_count(self) -> int:
            """Nonblank literal cell count."""
            ...

        @property
        def data_validation_count(self) -> int:
            """Data-validation rule count."""
            ...

        @property
        def conditional_format_count(self) -> int:
            """Conditional-format rule count."""
            ...

        @property
        def merge_count(self) -> int:
            """Merged-range count."""
            ...

    @runtime_checkable
    class XlsxWorkbookSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def data_only(self) -> bool:
            """Whether cells expose cached values."""
            ...

        @property
        def sheets(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxSheetSnapshot, ...]:
            """Exact worksheet order."""
            ...

        @property
        def defined_names(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxSnapshot.XlsxDefinedNameSnapshot, ...]:
            """Ordered defined names."""
            ...

        @property
        def named_styles(self) -> tuple[str, ...]:
            """Registered named styles."""
            ...

        @property
        def formula_count(self) -> int:
            """Workbook formula cell count."""
            ...

        @property
        def literal_count(self) -> int:
            """Workbook nonblank literal cell count."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxSnapshot",
]
