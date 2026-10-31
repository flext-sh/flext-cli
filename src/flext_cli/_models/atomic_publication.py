"""Atomic publication payload models for staged and observed filesystem state.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Literal

from flext_core import m, t

from flext_cli import c
from flext_cli._models._base.flextclimodelsbase_part_02 import FlextCliModelsBasePart02


class FlextCliModelsAtomicPublication:
    """Value-only payloads; live descriptor ownership stays with the utilities."""

    class StagedFile(m.ImmutableValueModel):
        """Exact staged pathname, bytes, mode and captured inode identity."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, strict=True)

        path: Path = m.Field(description="Exact pathname of the staged file.")
        content: bytes = m.Field(description="Authenticated staged file bytes.")
        mode: int = m.Field(description="Native permission mode of the staged file.")
        identity: tuple[int, int] = m.Field(
            description="Captured device and inode identity of the staged file.",
        )

    class ObservedFile(m.ImmutableValueModel):
        """An entry pathname and its unchanged native stat observation."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            frozen=True,
            strict=True,
        )

        path: Path = m.Field(description="Pathname of the observed file entry.")
        state: t.Port[os.stat_result] = m.Field(
            description="Unchanged native stat observation of the file entry.",
        )

    class AtomicWriteOptions(m.ImmutableValueModel):
        """Precondition, mode, durability and owner policy for one atomic write.

        ``expected_state`` is a complete physical precondition for a caller that
        holds the same exclusive cooperative lock from planning through
        publication; ``None`` publishes without a precondition. ``DURABLE`` syncs
        the staged inode and containing directory; ``SCRATCH`` keeps every atomic
        and physical check but skips both syncs for throwaway trees.
        """

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, strict=True)

        expected_state: FlextCliModelsBasePart02.AtomicFileState | None = m.Field(
            default=None,
            description="Complete physical precondition, or None for none.",
        )
        permission_mode: int | None = m.Field(
            default=None,
            description="Permission mode to publish, or None to keep the current one.",
        )
        durability: c.Cli.WriteDurability = m.Field(
            default=c.Cli.WriteDurability.DURABLE,
            description="Whether staged inode and parent directory are synced.",
        )
        owner_uid: int | None = m.Field(
            default=None,
            description="Required owner uid of the parent and published file.",
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


__all__: list[str] = ["FlextCliModelsAtomicPublication"]
