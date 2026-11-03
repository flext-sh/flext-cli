# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_05
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols


class FlextCliProtocolsBaseFlextclimodelsbasePart05:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class SettingsSnapshot(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def settings_dir(self) -> str:
            """Settings directory path."""
            ...

        @property
        def settings_exists(self) -> bool:
            """Whether settings directory exists."""
            ...

        @property
        def settings_readable(self) -> bool:
            """Whether settings directory is readable."""
            ...

        @property
        def settings_writable(self) -> bool:
            """Whether settings directory is writable."""
            ...

        @property
        def timestamp(self) -> str:
            """Timestamp of snapshot."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart05",
]
