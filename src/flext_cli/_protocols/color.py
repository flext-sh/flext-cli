# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/color
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable


class FlextCliProtocolsColor:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class RgbColor(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["rgb"]: ...
        @property
        def value(self) -> str: ...
        @property
        def tint(self) -> float: ...


__all__: list[str] = [
    "FlextCliProtocolsColor",
]
