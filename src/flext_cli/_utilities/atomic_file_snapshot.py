"""Public descriptor-authenticated snapshots composed from atomic file-state owners.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli._utilities import (
    atomic_file_descriptor as file_descriptor,
    atomic_file_path as file_path,
    atomic_file_state as file_state,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import t


def read_authenticated_state(
    path: Path,
    *,
    required: bool,
) -> t.Triple[os.stat_result | None, os.stat_result | None, bytes | None]:
    """Return one physical regular-file state or exact absence.

    An optional read of a path whose directory chain is not materialized is
    absence, not failure: the caller declared that absence is acceptable and no
    parent exists to authenticate, so the parent identity is absent too. A
    required read, and every write owner, still demand one physical, non-aliased
    parent directory.

    Returns:
        One physical regular-file state or exact absence.

    Raises:
        FileNotFoundError: If ``required``.

    """
    validated = file_path.validate_atomic_path(path)
    if not required and file_path.resolve_parent_path(validated.parent)[0] is None:
        return None, None, None
    with file_descriptor.parent_descriptor(validated) as parent:
        state = file_state.destination_state(validated, parent=parent)
        if state is None:
            if required:
                message = f"required atomic file is missing: {validated}"
                raise FileNotFoundError(errno.ENOENT, message, validated)
            file_descriptor.assert_parent_unchanged(parent)
            return parent.state, None, None
        content = file_state.read_authenticated_bytes(validated, state, parent=parent)
        return parent.state, state, content


__all__: list[str] = ["read_authenticated_state"]
