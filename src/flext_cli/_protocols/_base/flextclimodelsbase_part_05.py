# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_05
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsBaseFlextclimodelsbasePart05:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class SettingsSnapshot(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def settings_dir(self) -> str: ...
        @property
        def settings_exists(self) -> bool: ...
        @property
        def settings_readable(self) -> bool: ...
        @property
        def settings_writable(self) -> bool: ...
        @property
        def timestamp(self) -> str: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart05",
]
