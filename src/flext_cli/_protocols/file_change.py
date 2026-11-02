"""Structural contract for an authenticated planned file change."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliProtocolsFileChange:
    """Protocols mirrored from the file-change model module."""

    @runtime_checkable
    class FileChange(Protocol):
        """Observed file state and an intended content/mode replacement."""

        @property
        def path(self) -> Path:
            """Absolute destination path."""
            ...

        @property
        def before(self) -> p.Cli.AtomicFileState:
            """Authenticated state observed before publication."""
            ...

        @property
        def desired_content(self) -> bytes | None:
            """Desired content, or None for deletion."""
            ...

        @property
        def desired_mode(self) -> int | None:
            """Desired mode, or None for deletion."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsFileChange",)
