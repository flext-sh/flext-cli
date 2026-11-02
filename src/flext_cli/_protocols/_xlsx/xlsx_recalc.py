# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_recalc
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsXlsxXlsxRecalc:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxRecalcRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...

    @runtime_checkable
    class XlsxRecalcResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes: ...

    @runtime_checkable
    class XlsxRecalcParityRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...
        @property
        def expected_formula_count(self) -> int | None: ...

    @runtime_checkable
    class XlsxRecalcParityReport(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes: ...
        @property
        def recalculated(self) -> bool: ...
        @property
        def formula_count(self) -> int: ...
        @property
        def error_cells(self) -> tuple[str, ...]: ...
        @property
        def uncached_cells(self) -> tuple[str, ...]: ...
        @property
        def empty_result_cells(self) -> tuple[str, ...]: ...
        @property
        def ok(self) -> bool: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxRecalc",
]
