# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT CLI utility facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextUtilities

from flext_cli._utilities import (
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
    FlextCliUtilitiesAtomicTreeDarwin,
    FlextCliUtilitiesAtomicTreeDescriptor,
    FlextCliUtilitiesAtomicTreeInventory,
    FlextCliUtilitiesCli,
    FlextCliUtilitiesOptionBuilder,
)


class FlextCliUtilities(FlextUtilities):
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
        FlextCliUtilitiesAtomicTreeDarwin,
        FlextCliUtilitiesAtomicTreeDescriptor,
        FlextCliUtilitiesAtomicTreeInventory,
        FlextCliUtilitiesCli,
        FlextCliUtilitiesOptionBuilder,
    ):
        """CLI utility namespace."""


u = FlextCliUtilities
__all__: list[str] = ["FlextCliUtilities", "FlextCliUtilitiesCli", "u"]
