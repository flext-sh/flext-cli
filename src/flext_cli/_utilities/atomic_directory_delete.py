"""Guarded nonrecursive deletion owner for one physical empty directory.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from typing import TYPE_CHECKING

from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicDirectoryModel,
    FlextCliUtilitiesAtomicDirectoryState,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileRead,
)

if TYPE_CHECKING:
    from flext_cli import m


class FlextCliUtilitiesAtomicDirectoryDelete:
    """Canonical namespace owner."""

    @staticmethod
    def remove_guarded_empty_directory(state: m.Cli.AtomicDirectoryState) -> None:
        """Remove the exact empty-directory version authorized by the caller.

        Raises:
            OSError: If ``observed is None``; or if ``current is None or
            file_read.state_key(current) != file_read.state_key(authenticated)``; or if
            ``directory_state.destination_state(path, parent=parent) is not None``.

        """
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(state.path)
        FlextCliUtilitiesAtomicDirectoryModel.require_existing(state, purpose="deleted")
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_delete_capabilities(path)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(path) as parent:
            FlextCliUtilitiesAtomicDirectoryModel.require_parent(state, parent.state)
            observed = FlextCliUtilitiesAtomicDirectoryState.destination_state(
                path,
                parent=parent,
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_observed(state, observed)
            if observed is None:
                message = f"atomic directory disappeared before delete: {path}"
                raise OSError(errno.ESTALE, message, path)
            authenticated = FlextCliUtilitiesAtomicDirectoryState.read_empty_state(
                parent,
                path,
                observed,
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_observed(state, authenticated)
            current = FlextCliUtilitiesAtomicDirectoryState.destination_state(
                path,
                parent=parent,
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_observed(state, current)
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
                FlextCliUtilitiesAtomicDirectoryState.destination_state(
                    path,
                    parent=parent,
                )
                is not None
            ):
                message = f"atomic directory still exists after rmdir: {path}"
                raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryDelete"]
