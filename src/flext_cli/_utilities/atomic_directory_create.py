"""Guarded creation owner for one physical empty directory.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli import m, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryCleanup,
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicDirectoryModel,
    FlextCliUtilitiesAtomicDirectoryState,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFileMode,
    FlextCliUtilitiesAtomicFilePath,
)


class FlextCliUtilitiesAtomicDirectoryCreate:
    """Canonical namespace owner."""

    @staticmethod
    def create_guarded_empty_directory(
        before: m.Cli.AtomicDirectoryState,
        *,
        permission_mode: int,
    ) -> m.Cli.AtomicDirectoryState:
        """Create one directory only from an exact absent state under caller lock.

        Returns:
            The resulting ``m.Cli.AtomicDirectoryState``.

        Raises:
            OSError: If ``mode is None``.

        """
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(before.path)
        FlextCliUtilitiesAtomicDirectoryModel.require_absent(before, purpose="created")
        mode = FlextCliUtilitiesAtomicFileMode.validate_mode(
            permission_mode,
            label="permission_mode",
        )
        if mode is None:
            message = "permission_mode is required for atomic directory creation"
            raise OSError(errno.EINVAL, message, path)
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_create_capabilities(path)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(path) as parent:
            FlextCliUtilitiesAtomicDirectoryModel.require_parent(before, parent.state)
            observed = FlextCliUtilitiesAtomicDirectoryState.destination_state(
                path,
                parent=parent,
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_observed(before, observed)
            created = False
            identity: t.Pair[int, int] | None = None
            try:
                FlextCliUtilitiesAtomicDirectoryDescriptor.create_entry(parent, path)
                created = True
                initial = FlextCliUtilitiesAtomicDirectoryCreate._require_created_state(
                    parent,
                    path,
                )
                identity = (initial.st_dev, initial.st_ino)
                authenticated = (
                    FlextCliUtilitiesAtomicDirectoryCreate._initialize_created(
                        parent,
                        path,
                        initial,
                        identity,
                        mode,
                    )
                )
            except BaseException as operation_error:
                if created:
                    FlextCliUtilitiesAtomicDirectoryCleanup.remove_created_directory(
                        parent,
                        path,
                        identity,
                        operation_error,
                    )
                raise
            return FlextCliUtilitiesAtomicDirectoryModel.from_observed(
                path,
                parent.state,
                authenticated,
            )

    @staticmethod
    def _require_created_state(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
    ) -> os.stat_result:
        initial = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            path,
            parent=parent,
        )
        if initial is None:
            message = f"atomic directory missing immediately after mkdir: {path}"
            raise OSError(errno.ESTALE, message, path)
        return initial

    @staticmethod
    def _initialize_created(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        initial: os.stat_result,
        identity: t.Pair[int, int],
        mode: int,
    ) -> os.stat_result:
        final = FlextCliUtilitiesAtomicDirectoryState.initialize_empty_state(
            parent,
            path,
            initial,
            mode,
        )
        FlextCliUtilitiesAtomicDirectoryState.require_identity(path, final, identity)
        FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
        return FlextCliUtilitiesAtomicDirectoryState.read_empty_state(
            parent,
            path,
            final,
        )


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryCreate"]
