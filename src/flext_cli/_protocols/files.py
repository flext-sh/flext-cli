# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/files
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import p


class FlextCliProtocolsFiles:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class FileAssertionOptions(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def is_file(self) -> bool | None:
            """Require or reject a regular file; None leaves it unchecked."""
            ...

        @property
        def is_dir(self) -> bool | None:
            """Require or reject a directory; None leaves it unchecked."""
            ...

        @property
        def not_empty(self) -> bool | None:
            """Require non-empty file or directory contents when True."""
            ...

        @property
        def readable(self) -> bool | None:
            """Require read access to the path when True."""
            ...

        @property
        def writable(self) -> bool | None:
            """Require write access to the path when True."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsFiles",
]
