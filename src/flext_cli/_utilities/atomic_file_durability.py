"""Public directory durability for completed atomic namespace mutations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFilePath,
)


class FlextCliUtilitiesAtomicFileDurability:
    """Canonical namespace owner."""

    @staticmethod
    def sync_parent(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
    ) -> None:
        """Sync one authenticated directory after its namespace was mutated."""
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
        os.fsync(parent.descriptor)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)

    @staticmethod
    def sync_replacement(
        source: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        destination: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
    ) -> None:
        """Sync every physical directory changed by one completed replacement."""
        FlextCliUtilitiesAtomicFileDurability.sync_parent(source)
        if FlextCliUtilitiesAtomicFilePath.identity(
            source.state,
        ) != FlextCliUtilitiesAtomicFilePath.identity(destination.state):
            FlextCliUtilitiesAtomicFileDurability.sync_parent(destination)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileDurability"]
