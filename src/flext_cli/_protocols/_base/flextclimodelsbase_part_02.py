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


class FlextCliProtocolsBaseFlextclimodelsbasePart02:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class AtomicFileIdentity(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def parent_device(self) -> int | None: ...
        @property
        def parent_inode(self) -> int | None: ...
        @property
        def mode(self) -> int | None: ...
        @property
        def device(self) -> int | None: ...
        @property
        def inode(self) -> int | None: ...
        @property
        def link_count(self) -> int | None: ...
        @property
        def file_attributes(self) -> int | None: ...
        @property
        def reparse_tag(self) -> int | None: ...

    @runtime_checkable
    class AtomicFileState(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def parent_device(self) -> int | None: ...
        @property
        def parent_inode(self) -> int | None: ...
        @property
        def mode(self) -> int | None: ...
        @property
        def device(self) -> int | None: ...
        @property
        def inode(self) -> int | None: ...
        @property
        def link_count(self) -> int | None: ...
        @property
        def file_attributes(self) -> int | None: ...
        @property
        def reparse_tag(self) -> int | None: ...
        @property
        def content(self) -> bytes | None: ...

    @runtime_checkable
    class AtomicFileReceipt(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def parent_device(self) -> int | None: ...
        @property
        def parent_inode(self) -> int | None: ...
        @property
        def mode(self) -> int | None: ...
        @property
        def device(self) -> int | None: ...
        @property
        def inode(self) -> int | None: ...
        @property
        def link_count(self) -> int | None: ...
        @property
        def file_attributes(self) -> int | None: ...
        @property
        def reparse_tag(self) -> int | None: ...
        @property
        def size(self) -> int | None: ...
        @property
        def sha256(self) -> str | None: ...
        @property
        def version_key(self) -> tuple[int, ...] | None: ...

    @runtime_checkable
    class PromptRuntimeState(Protocol):
        """Structural data contract projected from the owning model."""

        interactive: bool
        quiet: bool
        default_timeout: int

    @runtime_checkable
    class AuthCredentialsPayload(Protocol):
        """Structural data contract projected from the owning model."""

        token: str | None
        username: str
        password: str

    @runtime_checkable
    class ProcessEnvironmentSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def base_env(self) -> Mapping[str, str]: ...
        @property
        def overrides(self) -> Mapping[str, str]: ...
        @property
        def remove_keys(self) -> Sequence[str]: ...
        @property
        def resolved(self) -> dict[str, str]: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart02",
]
