"""Public descriptor-authenticated snapshots composed from atomic file-state owners.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesAtomicFileSnapshot:
    """Canonical namespace owner."""

    @staticmethod
    def read_authenticated_state(
        path: Path,
        *,
        required: bool,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> t.Triple[os.stat_result | None, os.stat_result | None, bytes | None]:
        """Return one physical regular-file state or exact absence.

        ``owner_uid`` demands that the authenticated parent and the leaf, when
        present, belong to that uid. ``max_bytes`` rejects a leaf larger than the
        bound before its bytes are read and again after the bounded read.

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
        with FlextCliUtilitiesAtomicFileSnapshot.authenticated_entry(
            path, required=required, owner_uid=owner_uid, max_bytes=max_bytes
        ) as (parent, state):
            if parent is None or state is None:
                return None if parent is None else parent.state, None, None
            from flext_cli._utilities.atomic_file_state import (
                FlextCliUtilitiesAtomicFileState,
            )

            content = FlextCliUtilitiesAtomicFileState.read_authenticated_bytes(
                path, state, parent=parent
            )
            FlextCliUtilitiesAtomicFileSnapshot._require_size(
                path, len(content), max_bytes
            )
            return parent.state, state, content

    @staticmethod
    @contextmanager
    def authenticated_entry(
        path: Path,
        *,
        required: bool,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> Generator[
        tuple[
            FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor | None,
            os.stat_result | None,
        ]
    ]:
        """Retain one checked parent and leaf for the complete read operation."""
        validated = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(path)
        if (
            not required
            and FlextCliUtilitiesAtomicFilePath.resolve_parent_path(validated.parent)[0]
            is None
        ):
            yield None, None
            return
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            validated,
        ) as parent:
            FlextCliUtilitiesAtomicFileSnapshot._require_owner(
                validated.parent,
                parent.state,
                owner_uid,
            )
            from flext_cli._utilities.atomic_file_state import (
                FlextCliUtilitiesAtomicFileState,
            )

            state = FlextCliUtilitiesAtomicFileState.destination_state(
                validated,
                parent=parent,
            )
            if state is None:
                if required:
                    message = f"required atomic file is missing: {validated}"
                    raise FileNotFoundError(errno.ENOENT, message, validated)
            else:
                FlextCliUtilitiesAtomicFileSnapshot._require_owner(
                    validated, state, owner_uid
                )
                FlextCliUtilitiesAtomicFileSnapshot._require_size(
                    validated, state.st_size, max_bytes
                )
            yield parent, state
            FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                validated, state, parent=parent
            )
            FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)

    @staticmethod
    def _require_owner(
        path: Path,
        state: os.stat_result,
        owner_uid: int | None,
    ) -> None:
        """Reject one authenticated entry owned by another uid.

        Raises:
            PermissionError: If ``state`` is not owned by ``owner_uid``.

        """
        if owner_uid is not None and state.st_uid != owner_uid:
            message = f"atomic path owner {state.st_uid} is not {owner_uid}: {path}"
            raise PermissionError(errno.EPERM, message, path)

    @staticmethod
    def _require_size(path: Path, size: int, max_bytes: int | None) -> None:
        """Reject one leaf larger than the declared bound.

        Raises:
            OSError: If ``size`` exceeds ``max_bytes``.

        """
        if max_bytes is not None and size > max_bytes:
            message = f"atomic file exceeds {max_bytes} bytes: {path}"
            raise OSError(errno.EFBIG, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileSnapshot"]
