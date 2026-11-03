# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_recalc
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols


class FlextCliProtocolsXlsxXlsxRecalc:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxRecalcRequest(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Source workbook bytes."""
            ...

    @runtime_checkable
    class XlsxRecalcResult(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes:
            """Recalculated workbook bytes."""
            ...

    @runtime_checkable
    class XlsxRecalcParityRequest(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Source workbook bytes."""
            ...

        @property
        def expected_formula_count(self) -> int | None:
            """Expected source formula cell count."""
            ...

    @runtime_checkable
    class XlsxRecalcParityReport(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes:
            """Exact recalculated workbook bytes validated by this report."""
            ...

        @property
        def recalculated(self) -> bool:
            """Whether the engine produced recalculated bytes."""
            ...

        @property
        def formula_count(self) -> int:
            """Source workbook formula cell count."""
            ...

        @property
        def error_cells(self) -> tuple[str, ...]:
            """Formula cells whose cached value is an error literal."""
            ...

        @property
        def uncached_cells(self) -> tuple[str, ...]:
            """Formula cells without any cached value element."""
            ...

        @property
        def empty_result_cells(self) -> tuple[str, ...]:
            """Formula cells cached as an empty string result."""
            ...

        @property
        def ok(self) -> bool:
            """Structural member projected from the owning model.

            Producer-stored verdict: caches complete, no errors, count matches.
            """
            ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxRecalc",
]
