"""Structural contract for an authenticated planned file change.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart02


class FlextCliProtocolsFileChange:
    """Protocols mirrored from the file-change model module."""

    @runtime_checkable
    class FileChange(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Absolute destination path."""
            ...

        @property
        def before(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Destination state observed while planning."""
            ...

        @property
        def desired_content(self) -> bytes | None:
            """Desired bytes, or None to delete."""
            ...

        @property
        def desired_mode(self) -> int | None:
            """Desired mode, or None with deletion."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsFileChange",)
