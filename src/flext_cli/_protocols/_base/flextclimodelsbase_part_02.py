# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_02
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols


class FlextCliProtocolsBaseFlextclimodelsbasePart02:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicFileIdentity(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Absolute file path."""
            ...

        @property
        def parent_device(self) -> int | None:
            """Physical parent device, or None when the chain is absent."""
            ...

        @property
        def parent_inode(self) -> int | None:
            """Physical parent inode, or None when the chain is absent."""
            ...

        @property
        def mode(self) -> int | None:
            """Exact permission bits, or None when absent."""
            ...

        @property
        def device(self) -> int | None:
            """Physical device, or None when absent."""
            ...

        @property
        def inode(self) -> int | None:
            """Physical inode, or None when absent."""
            ...

        @property
        def link_count(self) -> int | None:
            """Observed link count (>= 1), or None when absent."""
            ...

        @property
        def file_attributes(self) -> int | None:
            """Host file attributes when available."""
            ...

        @property
        def reparse_tag(self) -> int | None:
            """Host reparse tag when available."""
            ...

    @runtime_checkable
    class AtomicFileState(AtomicFileIdentity, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes | None:
            """Exact bytes, or None when absent."""
            ...

    @runtime_checkable
    class AtomicFileReceipt(AtomicFileIdentity, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def size(self) -> int | None:
            """Exact byte length."""
            ...

        @property
        def sha256(self) -> str | None:
            """Digest of the complete authenticated descriptor."""
            ...

        @property
        def version_key(self) -> tuple[int, ...] | None:
            """Native descriptor version used for guarded reads."""
            ...

    @runtime_checkable
    class PromptRuntimeState(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        interactive: bool
        quiet: bool
        default_timeout: int

    @runtime_checkable
    class AuthCredentialsPayload(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        token: str | None
        username: str
        password: str

    @runtime_checkable
    class ProcessEnvironmentSpec(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def base_env(self) -> Mapping[str, str]:
            """Base environment inherited from the current process."""
            ...

        @property
        def overrides(self) -> Mapping[str, str]:
            """Explicit environment overrides for the child process."""
            ...

        @property
        def remove_keys(self) -> Sequence[str]:
            """Environment keys removed before applying overrides."""
            ...

        @property
        def resolved(self) -> dict[str, str]:
            """Resolved environment mapping after removals and overrides."""
            ...

        def resolve(self) -> dict[str, str]:
            """Type-safe accessor for the computed environment mapping."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart02",
]
