"""Guarded creation owner for one physical empty directory."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli import m

from . import (
    atomic_directory_cleanup as directory_cleanup,
    atomic_directory_descriptor as directory_descriptor,
    atomic_directory_model as directory_model,
    atomic_directory_state as directory_state,
    atomic_file_descriptor as file_descriptor,
    atomic_file_durability as file_durability,
    atomic_file_mode as file_mode,
    atomic_file_path as file_path,
)


def create_guarded_empty_directory(
    before: m.Cli.AtomicDirectoryState, *, permission_mode: int
) -> m.Cli.AtomicDirectoryState:
    """Create one directory only from an exact absent state under caller lock."""
    path = file_path.validate_atomic_path(before.path)
    directory_model.require_absent(before, purpose="created")
    mode = file_mode.validate_mode(permission_mode, label="permission_mode")
    if mode is None:
        message = "permission_mode is required for atomic directory creation"
        raise OSError(errno.EINVAL, message, path)
    directory_descriptor.require_create_capabilities(path)
    with file_descriptor.parent_descriptor(path) as parent:
        directory_model.require_parent(before, parent.state)
        observed = directory_state.destination_state(path, parent=parent)
        directory_model.require_observed(before, observed)
        created = False
        identity: tuple[int, int] | None = None
        try:
            directory_descriptor.create_entry(parent, path)
            created = True
            initial = _require_created_state(parent, path)
            identity = (initial.st_dev, initial.st_ino)
            authenticated = _initialize_created(parent, path, initial, identity, mode)
        except BaseException as operation_error:
            if created:
                directory_cleanup.remove_created_directory(
                    parent, path, identity, operation_error
                )
            raise
        return directory_model.from_observed(path, parent.state, authenticated)


def _require_created_state(
    parent: file_descriptor.ParentDescriptor, path: Path
) -> os.stat_result:
    initial = directory_state.destination_state(path, parent=parent)
    if initial is None:
        message = f"atomic directory missing immediately after mkdir: {path}"
        raise OSError(errno.ESTALE, message, path)
    return initial


def _initialize_created(
    parent: file_descriptor.ParentDescriptor,
    path: Path,
    initial: os.stat_result,
    identity: tuple[int, int],
    mode: int,
) -> os.stat_result:
    final = directory_state.initialize_empty_state(parent, path, initial, mode)
    directory_state.require_identity(path, final, identity)
    file_durability.sync_parent(parent)
    return directory_state.read_empty_state(parent, path, final)


__all__: list[str] = ["create_guarded_empty_directory"]
