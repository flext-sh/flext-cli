# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/color
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from flext_core import p


class FlextCliProtocolsColor:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class RgbColor(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["rgb"]:
            """Color kind."""
            ...

        @property
        def value(self) -> str:
            """RGB or ARGB value."""
            ...

        @property
        def tint(self) -> float:
            """Color tint."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsColor",
]
