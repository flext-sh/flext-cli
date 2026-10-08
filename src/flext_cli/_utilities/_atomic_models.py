"""Private value contexts for atomic publication and tree inventory.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Literal

from flext_core import m, t


class FlextCliAtomicModels:
    """Value-only contexts; live descriptor ownership stays with the utilities."""

    class StagedFile(m.ImmutableValueModel):
        """Exact staged pathname, bytes, mode and captured inode identity."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, strict=True)

        path: Path = m.Field(description="Exact pathname of the staged file.")
        content: bytes = m.Field(description="Authenticated staged file bytes.")
        mode: int = m.Field(description="Native permission mode of the staged file.")
        identity: t.Pair[int, int] = m.Field(
            description="Captured device and inode identity of the staged file.",
        )

    class ObservedFile(m.ImmutableValueModel):
        """An entry pathname and its unchanged native stat observation."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            frozen=True,
            strict=True,
            arbitrary_types_allowed=True,
        )

        path: Path = m.Field(description="Pathname of the observed file entry.")
        state: os.stat_result = m.Field(
            description="Unchanged native stat observation of the file entry.",
        )

    class TreeEntryDetails(m.ImmutableValueModel):
        """Measured kind-specific data and mount bindings for one tree entry."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, strict=True)

        kind: Literal["directory", "file", "symlink"] = m.Field(
            description="Measured filesystem kind of the tree entry.",
        )
        parent_mount_id: int = m.Field(
            description="Mount identity of the parent entry.",
        )
        mount_id: int = m.Field(description="Mount identity of the tree entry.")
        size: int | None = m.Field(default=None, description="Measured file byte size.")
        digest: str | None = m.Field(
            default=None,
            description="Authenticated content digest for a regular file.",
        )
        link_target: str | None = m.Field(
            default=None,
            description="Literal target of a symbolic link entry.",
        )
