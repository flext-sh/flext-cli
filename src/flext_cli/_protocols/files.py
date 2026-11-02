# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/files
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsFiles:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class FileAssertionOptions(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def is_file(self) -> bool | None: ...
        @property
        def is_dir(self) -> bool | None: ...
        @property
        def not_empty(self) -> bool | None: ...
        @property
        def readable(self) -> bool | None: ...
        @property
        def writable(self) -> bool | None: ...


__all__: list[str] = [
    "FlextCliProtocolsFiles",
]
