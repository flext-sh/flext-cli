"""Guarded nonrecursive deletion owner for one physical empty directory.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno

from flext_cli import p
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicDirectoryModel,
    FlextCliUtilitiesAtomicDirectoryState,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileRead,
)


class FlextCliUtilitiesAtomicDirectoryDelete:
    """Canonical namespace owner."""

    @staticmethod
    def remove_guarded_empty_directory(state: p.Cli.AtomicDirectoryState) -> None:
        """Remove the exact empty-directory version authorized by the caller.

        Raises:
            OSError: If ``observed is None``; or if ``current is None or
            file_read.state_key(current) != file_read.state_key(authenticated)``; or if
            ``directory_state.directory_destination_state(path, parent=parent)
            is not None``.

        """
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(state.path)
        FlextCliUtilitiesAtomicDirectoryModel.require_directory_existing(
            state, purpose="deleted"
        )
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_delete_capabilities(path)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(path) as parent:
            FlextCliUtilitiesAtomicDirectoryModel.require_directory_parent(
                state, parent.state
            )
            observed = (
                FlextCliUtilitiesAtomicDirectoryState.directory_destination_state(
                    path,
                    parent=parent,
                )
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_directory_observed(
                state, observed
            )
            if observed is None:
                message = f"atomic directory disappeared before delete: {path}"
                raise OSError(errno.ESTALE, message, path)
            authenticated = FlextCliUtilitiesAtomicDirectoryState.read_empty_state(
                parent,
                path,
                observed,
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_directory_observed(
                state, authenticated
            )
            current = FlextCliUtilitiesAtomicDirectoryState.directory_destination_state(
                path,
                parent=parent,
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_directory_observed(
                state, current
            )
            if current is None or FlextCliUtilitiesAtomicFileRead.state_key(
                current,
            ) != FlextCliUtilitiesAtomicFileRead.state_key(
                authenticated,
            ):
                message = f"atomic directory changed immediately before rmdir: {path}"
                raise OSError(errno.ESTALE, message, path)
            FlextCliUtilitiesAtomicDirectoryDescriptor.remove_entry(parent, path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            if (
                FlextCliUtilitiesAtomicDirectoryState.directory_destination_state(
                    path,
                    parent=parent,
                )
                is not None
            ):
                message = f"atomic directory still exists after rmdir: {path}"
                raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryDelete"]
