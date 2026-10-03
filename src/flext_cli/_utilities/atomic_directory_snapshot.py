"""Public snapshot owner for descriptor-authenticated empty directories.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import atomic_directory_descriptor
from flext_cli._utilities import atomic_directory_model
from flext_cli._utilities import atomic_directory_state
from flext_cli._utilities import atomic_file_descriptor
from flext_cli._utilities import atomic_file_path

if TYPE_CHECKING:
    from flext_cli import m



def read_authenticated_empty_directory(
    path: Path,
    *,
    required: bool,
) -> m.Cli.AtomicDirectoryState:
    """Return exact absence or one stable, physical, empty directory state.

    An optional read of a path whose directory chain is not materialized is
    absence, not failure: no parent exists to authenticate, so the parent
    identity is absent too. A required read, and every write owner, still demand
    one physical, non-aliased parent directory.

    Returns:
        Exact absence or one stable, physical, empty directory state.

    Raises:
        FileNotFoundError: If ``required``.

    """
    path = atomic_file_path.validate_atomic_path(path)
    atomic_directory_descriptor.require_read_capabilities(path)
    if (
        not required
        and atomic_file_path.resolve_parent_path(path.parent)[0]
        is None
    ):
        return atomic_directory_model.from_observed(path, None, None)
    with atomic_file_descriptor.parent_descriptor(path) as parent:
        observed = atomic_directory_state.destination_state(
            path, parent=parent,
        )
        if observed is None:
            if required:
                message = f"required atomic directory is missing: {path}"
                raise FileNotFoundError(errno.ENOENT, message, path)
            atomic_file_descriptor.assert_parent_unchanged(parent)
            return atomic_directory_model.from_observed(
                path, parent.state, None,
            )
        authenticated = atomic_directory_state.read_empty_state(
            parent, path, observed,
        )
        return atomic_directory_model.from_observed(
            path, parent.state, authenticated,
        )


__all__: list[str] = [
    "read_authenticated_empty_directory",
]
