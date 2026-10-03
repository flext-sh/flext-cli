"""Guarded nonrecursive deletion owner for one physical empty directory.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from typing import TYPE_CHECKING

from flext_cli._utilities.atomic_directory_descriptor import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
)
from flext_cli._utilities import atomic_directory_model
from flext_cli._utilities import atomic_directory_state
from flext_cli._utilities import atomic_file_descriptor
from flext_cli._utilities.atomic_file_durability import (
    FlextCliUtilitiesAtomicFileDurability,
)
from flext_cli._utilities import atomic_file_path
from flext_cli._utilities import atomic_file_read

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
        path = atomic_file_path.validate_atomic_path(state.path)
        atomic_directory_model.require_existing(state, purpose="deleted")
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_delete_capabilities(path)
        with atomic_file_descriptor.parent_descriptor(path) as parent:
            atomic_directory_model.require_parent(state, parent.state)
            observed = atomic_directory_state.destination_state(
                path, parent=parent,
            )
            atomic_directory_model.require_observed(state, observed)
            if observed is None:
                message = f"atomic directory disappeared before delete: {path}"
                raise OSError(errno.ESTALE, message, path)
            authenticated = atomic_directory_state.read_empty_state(
                parent, path, observed,
            )
            atomic_directory_model.require_observed(state, authenticated)
            current = atomic_directory_state.destination_state(
                path, parent=parent,
            )
            atomic_directory_model.require_observed(state, current)
            if current is None or atomic_file_read.state_key(
                current,
            ) != atomic_file_read.state_key(
                authenticated,
            ):
                message = f"atomic directory changed immediately before rmdir: {path}"
                raise OSError(errno.ESTALE, message, path)
            FlextCliUtilitiesAtomicDirectoryDescriptor.remove_entry(parent, path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            if (
                atomic_directory_state.destination_state(
                    path, parent=parent,
                )
                is not None
            ):
                message = f"atomic directory still exists after rmdir: {path}"
                raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryDelete"]
