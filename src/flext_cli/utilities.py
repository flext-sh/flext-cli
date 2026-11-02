# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT CLI utility facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeAlias

from flext_core import u as flext_core_u

from flext_cli._utilities import (
    FlextCliAtomicTreeDarwin,
    FlextCliUtilitiesAtomicDirectoryChain,
    FlextCliUtilitiesAtomicDirectoryCleanup,
    FlextCliUtilitiesAtomicDirectoryCreate,
    FlextCliUtilitiesAtomicDirectoryDelete,
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicDirectoryModel,
    FlextCliUtilitiesAtomicDirectoryNoreplace,
    FlextCliUtilitiesAtomicDirectoryPublish,
    FlextCliUtilitiesAtomicDirectorySnapshot,
    FlextCliUtilitiesAtomicDirectoryState,
    FlextCliUtilitiesAtomicFile,
    FlextCliUtilitiesAtomicFileCleanup,
    FlextCliUtilitiesAtomicFileDelete,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFileMode,
    FlextCliUtilitiesAtomicFileModel,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFilePublish,
    FlextCliUtilitiesAtomicFilePublishChecks,
    FlextCliUtilitiesAtomicFileRead,
    FlextCliUtilitiesAtomicFileSnapshot,
    FlextCliUtilitiesAtomicFileState,
    FlextCliUtilitiesAtomicFileTemporary,
    FlextCliUtilitiesAtomicParentDescriptor,
    FlextCliUtilitiesAtomicParentFailure,
    FlextCliUtilitiesAtomicSymlinkPublish,
    FlextCliUtilitiesAtomicSymlinkState,
    FlextCliUtilitiesAtomicTreeCleanup,
    FlextCliUtilitiesAtomicTreeDescriptor,
    FlextCliUtilitiesAtomicTreeInventory,
    FlextCliUtilitiesBase,
    FlextCliUtilitiesCli,
    FlextCliUtilitiesOptionBuilder,
    RuntimeSpawnOptions,
)


class FlextCliUtilities(flext_core_u):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(
        FlextCliUtilitiesAtomicDirectoryChain,
        FlextCliUtilitiesAtomicDirectoryCleanup,
        FlextCliUtilitiesAtomicDirectoryCreate,
        FlextCliUtilitiesAtomicDirectoryDelete,
        FlextCliUtilitiesAtomicDirectoryDescriptor,
        FlextCliUtilitiesAtomicDirectoryModel,
        FlextCliUtilitiesAtomicDirectoryNoreplace,
        FlextCliUtilitiesAtomicDirectoryPublish,
        FlextCliUtilitiesAtomicDirectorySnapshot,
        FlextCliUtilitiesAtomicDirectoryState,
        FlextCliUtilitiesAtomicFile,
        FlextCliUtilitiesAtomicFileCleanup,
        FlextCliUtilitiesAtomicFileDelete,
        FlextCliUtilitiesAtomicFileDescriptor,
        FlextCliUtilitiesAtomicFileDurability,
        FlextCliUtilitiesAtomicFileMode,
        FlextCliUtilitiesAtomicFileModel,
        FlextCliUtilitiesAtomicFilePath,
        FlextCliUtilitiesAtomicFilePublish,
        FlextCliUtilitiesAtomicFilePublishChecks,
        FlextCliUtilitiesAtomicFileRead,
        FlextCliUtilitiesAtomicFileSnapshot,
        FlextCliUtilitiesAtomicFileState,
        FlextCliUtilitiesAtomicFileTemporary,
        FlextCliUtilitiesAtomicParentDescriptor,
        FlextCliUtilitiesAtomicParentFailure,
        FlextCliUtilitiesAtomicSymlinkPublish,
        FlextCliUtilitiesAtomicSymlinkState,
        FlextCliUtilitiesAtomicTreeCleanup,
        FlextCliAtomicTreeDarwin,
        FlextCliUtilitiesAtomicTreeDescriptor,
        FlextCliUtilitiesAtomicTreeInventory,
        FlextCliUtilitiesBase,
        FlextCliUtilitiesCli,
        FlextCliUtilitiesOptionBuilder,
    ):
        """CLI utility namespace."""

        RuntimeSpawnOptions: TypeAlias = RuntimeSpawnOptions


u = FlextCliUtilities
__all__: list[str] = ["FlextCliUtilities", "FlextCliUtilitiesCli", "u"]
