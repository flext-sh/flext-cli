"""Public descriptor-authenticated snapshots composed from atomic file-state owners.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesAtomicFileSnapshot:
    """Canonical namespace owner."""

    @staticmethod
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
        validated = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(path)
        if (
            not required
            and FlextCliUtilitiesAtomicFilePath.resolve_parent_path(validated.parent)[0]
            is None
        ):
            return None, None, None
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            validated,
        ) as parent:
            state = FlextCliUtilitiesAtomicFileState.destination_state(
                validated,
                parent=parent,
            )
            if state is None:
                if required:
                    message = f"required atomic file is missing: {validated}"
                    raise FileNotFoundError(errno.ENOENT, message, validated)
                FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
                return parent.state, None, None
            content = FlextCliUtilitiesAtomicFileState.read_authenticated_bytes(
                validated,
                state,
                parent=parent,
            )
            return parent.state, state, content


__all__: list[str] = ["FlextCliUtilitiesAtomicFileSnapshot"]
