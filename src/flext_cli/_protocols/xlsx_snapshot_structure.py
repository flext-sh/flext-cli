"""Structural protocols for XLSX sheet snapshot evidence.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsXlsxSnapshotStructure:
    """Typed structural evidence retained from worksheet XML."""

    @runtime_checkable
    class XlsxDimensionSnapshot(Protocol):
        """Shared layout-state evidence retained for one worksheet dimension."""

        @property
        def size(self) -> float | None: ...

        @property
        def hidden(self) -> bool: ...

        @property
        def outline_level(self) -> int | None: ...


__all__: tuple[str, ...] = ("FlextCliProtocolsXlsxSnapshotStructure",)
