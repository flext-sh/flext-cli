"""Descriptor-authenticated snapshots composed from atomic file-state owners."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli._utilities import _atomic_file_descriptor as file_descriptor
from flext_cli._utilities import _atomic_file_state as file_state


def read_authenticated_state(
    path: Path, *, required: bool
) -> tuple[os.stat_result | None, bytes | None]:
    """Return one physical regular-file state or exact absence."""
    with file_descriptor.parent_descriptor(path) as parent:
        state = file_state.destination_state(path, parent=parent)
        if state is None:
            if required:
                message = f"required atomic file is missing: {path}"
                raise FileNotFoundError(errno.ENOENT, message, path)
            file_descriptor.assert_parent_unchanged(parent)
            return None, None
        content = file_state.read_authenticated_bytes(path, state, parent=parent)
        return state, content


__all__: list[str] = ["read_authenticated_state"]
