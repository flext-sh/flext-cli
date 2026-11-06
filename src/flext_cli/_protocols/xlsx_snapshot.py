"""Structural contracts for typed XLSX semantic snapshots.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli._protocols import FlextCliProtocolsXlsxSnapshotStructure

if TYPE_CHECKING:
    from flext_core import p

    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxSnapshot


class FlextCliProtocolsXlsxSnapshot(FlextCliProtocolsXlsxSnapshotStructure):
    """Consumer-facing protocols for workbook parity evidence."""

    # NOTE (multi-agent, mro-j2yt.1): protocols expose the original immutable
    # snapshot models directly; no mapping or revalidation boundary is added.

    @runtime_checkable
    class XlsxSnapshotService(Protocol):
        def xlsx_snapshot(
            self,
            request: FlextCliProtocolsXlsxXlsxSnapshot.XlsxSnapshotRequest,
        ) -> p.Result[FlextCliProtocolsXlsxXlsxSnapshot.XlsxWorkbookSnapshot]: ...

        def xlsx_defined_name_values(
            self,
            request: FlextCliProtocolsXlsxXlsxSnapshot.XlsxDefinedNameValuesRequest,
        ) -> p.Result[
            FlextCliProtocolsXlsxXlsxSnapshot.XlsxDefinedNameValuesResult
        ]: ...


__all__: tuple[str, ...] = ("FlextCliProtocolsXlsxSnapshot",)
