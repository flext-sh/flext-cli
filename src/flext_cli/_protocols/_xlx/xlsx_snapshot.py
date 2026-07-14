"""Structural contracts for typed XLSX semantic snapshots."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import p

from .xlsx_snapshot_structure import FlextCliProtocolsXlsxSnapshotStructure


class FlextCliProtocolsXlsxSnapshot(FlextCliProtocolsXlsxSnapshotStructure):
    """Consumer-facing protocols for workbook parity evidence."""

    # mro-wkii.17.26 (codex): snapshot relations stay structural inside p;
    # concrete XLSX models are construction outputs and cannot be p dependencies.
    @runtime_checkable
    class XlsxCellAddress(Protocol):
        @property
        def row(self) -> int: ...

        @property
        def column(self) -> int: ...

    @runtime_checkable
    class XlsxCellValue(Protocol):
        @property
        def kind(self) -> str: ...

    # NOTE (multi-agent, mro-j2yt.1): protocols expose the original immutable
    # snapshot models directly; no mapping or revalidation boundary is added.
    @runtime_checkable
    class XlsxSnapshotRequest(Protocol):
        @property
        def source(self) -> bytes: ...

        @property
        def data_only(self) -> bool: ...

    @runtime_checkable
    class XlsxCellSnapshot(Protocol):
        @property
        def coordinate(self) -> str: ...

        @property
        def position(self) -> FlextCliProtocolsXlsxSnapshot.XlsxCellAddress: ...

        @property
        def value(self) -> FlextCliProtocolsXlsxSnapshot.XlsxCellValue: ...

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
        @property
        def name(self) -> str: ...

        @property
        def reference(self) -> str: ...

        @property
        def style_name(self) -> str | None: ...

    @runtime_checkable
    class XlsxDefinedNameSnapshot(Protocol):
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
    class XlsxSheetSnapshot(Protocol):
        @property
        def name(self) -> str: ...

        @property
        def position(self) -> int: ...

        @property
        def state(self) -> str: ...

        @property
        def max_row(self) -> int: ...

        @property
        def max_column(self) -> int: ...

        @property
        def cells(
            self,
        ) -> tuple[FlextCliProtocolsXlsxSnapshot.XlsxCellSnapshot, ...]: ...

        @property
        def tables(
            self,
        ) -> tuple[FlextCliProtocolsXlsxSnapshot.XlsxTableSnapshot, ...]: ...

        @property
        def row_dimensions(
            self,
        ) -> tuple[FlextCliProtocolsXlsxSnapshot.XlsxRowDimensionSnapshot, ...]: ...

        @property
        def column_dimensions(
            self,
        ) -> tuple[FlextCliProtocolsXlsxSnapshot.XlsxColumnDimensionSnapshot, ...]: ...

        @property
        def merged_ranges(self) -> tuple[str, ...]: ...

        @property
        def freeze_pane(self) -> str | None: ...

        @property
        def auto_filter(self) -> str | None: ...

        @property
        def protection(
            self,
        ) -> FlextCliProtocolsXlsxSnapshot.XlsxSheetProtectionSnapshot: ...

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
        @property
        def data_only(self) -> bool: ...

        @property
        def sheets(
            self,
        ) -> tuple[FlextCliProtocolsXlsxSnapshot.XlsxSheetSnapshot, ...]: ...

        @property
        def defined_names(
            self,
        ) -> tuple[FlextCliProtocolsXlsxSnapshot.XlsxDefinedNameSnapshot, ...]: ...

        @property
        def named_styles(self) -> tuple[str, ...]: ...

        @property
        def formula_count(self) -> int: ...

        @property
        def literal_count(self) -> int: ...

    @runtime_checkable
    class XlsxSnapshotService(Protocol):
        def xlsx_snapshot(
            self, request: FlextCliProtocolsXlsxSnapshot.XlsxSnapshotRequest
        ) -> p.Result[FlextCliProtocolsXlsxSnapshot.XlsxWorkbookSnapshot]: ...


__all__: tuple[str, ...] = ("FlextCliProtocolsXlsxSnapshot",)
