"""Public snapshot owner for descriptor-authenticated empty directories."""

from __future__ import annotations

import errno
from pathlib import Path

from flext_cli import m
from . import atomic_directory_descriptor as directory_descriptor
from . import atomic_directory_model as directory_model
from . import atomic_directory_state as directory_state
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_path as file_path


def read_authenticated_empty_directory(
    path: Path, *, required: bool
) -> m.Cli.AtomicDirectoryState:
    """Return exact absence or one stable, physical, empty directory state."""
    path = file_path.validate_atomic_path(path)
    directory_descriptor.require_read_capabilities(path)
    with file_descriptor.parent_descriptor(path) as parent:
        observed = directory_state.destination_state(path, parent=parent)
        if observed is None:
            if required:
                message = f"required atomic directory is missing: {path}"
                raise FileNotFoundError(errno.ENOENT, message, path)
            file_descriptor.assert_parent_unchanged(parent)
            return directory_model.from_observed(path, parent.state, None)
        authenticated = directory_state.read_empty_state(parent, path, observed)
        return directory_model.from_observed(path, parent.state, authenticated)


__all__: list[str] = ["read_authenticated_empty_directory"]
