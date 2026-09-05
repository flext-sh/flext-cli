"""Guarded nonrecursive deletion owner for one physical empty directory."""

from __future__ import annotations

import errno

from flext_cli import m
from . import atomic_directory_descriptor as directory_descriptor
from . import atomic_directory_model as directory_model
from . import atomic_directory_state as directory_state
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_durability as file_durability
from . import atomic_file_path as file_path
from . import atomic_file_read as file_read


def remove_guarded_empty_directory(state: m.Cli.AtomicDirectoryState) -> None:
    """Remove the exact empty-directory version authorized by the caller."""
    path = file_path.validate_atomic_path(state.path)
    directory_model.require_existing(state, purpose="deleted")
    directory_descriptor.require_delete_capabilities(path)
    with file_descriptor.parent_descriptor(path) as parent:
        directory_model.require_parent(state, parent.state)
        observed = directory_state.destination_state(path, parent=parent)
        directory_model.require_observed(state, observed)
        if observed is None:
            message = f"atomic directory disappeared before delete: {path}"
            raise OSError(errno.ESTALE, message, path)
        authenticated = directory_state.read_empty_state(parent, path, observed)
        directory_model.require_observed(state, authenticated)
        current = directory_state.destination_state(path, parent=parent)
        directory_model.require_observed(state, current)
        if current is None or file_read.state_key(current) != file_read.state_key(
            authenticated
        ):
            message = f"atomic directory changed immediately before rmdir: {path}"
            raise OSError(errno.ESTALE, message, path)
        directory_descriptor.remove_entry(parent, path)
        file_durability.sync_parent(parent)
        if directory_state.destination_state(path, parent=parent) is not None:
            message = f"atomic directory still exists after rmdir: {path}"
            raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["remove_guarded_empty_directory"]
