# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/table_render
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols


class FlextCliProtocolsTableRender:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class TableColumnPolicy(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def headers(self) -> str | tuple[str, ...]:
            """Header mode (``firstrow``/``keys``) or explicit labels."""
            ...

        @property
        def colalign(self) -> tuple[str, ...]:
            """Per-column alignment overrides, in column order."""
            ...

    @runtime_checkable
    class TableLayout(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def cells(self) -> tuple[tuple[str, ...], ...]:
            """Formatted body cells, one tuple per row."""
            ...

        @property
        def header_labels(self) -> tuple[str, ...]:
            """Header labels in column order."""
            ...

        @property
        def widths(self) -> tuple[int, ...]:
            """Display width of every column."""
            ...

        @property
        def alignments(self) -> tuple[str, ...]:
            """Resolved padding alignment of every column."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsTableRender",
]
