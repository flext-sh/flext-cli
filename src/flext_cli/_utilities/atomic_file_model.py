"""Public typed physical-state authentication for atomic file snapshots.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli.typings import PhysicalState

if TYPE_CHECKING:
    from flext_cli import m, t


class FlextCliUtilitiesAtomicFileModel:
    """Canonical namespace owner."""

    @staticmethod
    def require_existing(
        state: m.Cli.AtomicFileState,
        *,
        purpose: str,
    ) -> t.Triple[bytes, int, t.Pair[int, int]]:
        """Return required content, mode, and inode identity from an existing state.

        Returns:
            Required content, mode, and inode identity from an existing state.

        Raises:
            FileNotFoundError: If ``state.content is None or state.mode is None or
                state.device is None or (state.inode is None) or (state.link_count is
                None)``.

        """
        if (
            state.content is None
            or state.mode is None
            or state.device is None
            or state.inode is None
            or state.link_count is None
        ):
            message = f"{purpose} atomic file state is absent: {state.path}"
            raise FileNotFoundError(errno.ENOENT, message, state.path)
        return state.content, state.mode, (state.device, state.inode)

    @staticmethod
    def require_observed(
        planned: m.Cli.AtomicFileState,
        observed: os.stat_result | None,
        *,
        path: Path | None = None,
    ) -> None:
        """Require host metadata to equal every available planned physical field.

        Raises:
            OSError: If ``observed is None``; or if ``expected !=
                physical_state(observed)``; or if ``observed is not None``.

        """
        target = planned.path if path is None else path
        if planned.content is None:
            if observed is not None:
                message = f"atomic file appeared after absent snapshot: {target}"
                raise OSError(errno.ESTALE, message, target)
            return
        if observed is None:
            message = f"atomic file disappeared after snapshot: {target}"
            raise OSError(errno.ESTALE, message, target)
        expected = FlextCliUtilitiesAtomicFileModel._planned_physical_state(planned)
        if expected != FlextCliUtilitiesAtomicFileModel.physical_state(observed):
            message = f"atomic file physical state changed: {target}"
            raise OSError(errno.ESTALE, message, target)

    @staticmethod
    def require_parent(state: m.Cli.AtomicFileState, observed: os.stat_result) -> None:
        """Require the authenticated parent to equal the snapshot parent identity.

        Raises:
            FileNotFoundError: If ``state.parent_device is None or state.parent_inode is
                None``.
            OSError: If ``(state.parent_device, state.parent_inode) != (observed.st_dev,
                observed.st_ino)``.

        """
        if state.parent_device is None or state.parent_inode is None:
            message = f"atomic file parent was absent at snapshot: {state.path.parent}"
            raise FileNotFoundError(errno.ENOENT, message, state.path.parent)
        if (state.parent_device, state.parent_inode) != (
            observed.st_dev,
            observed.st_ino,
        ):
            message = f"atomic file parent identity changed: {state.path.parent}"
            raise OSError(errno.ESTALE, message, state.path.parent)

    @staticmethod
    def physical_state(state: os.stat_result) -> PhysicalState:
        """Return every caller-visible physical identity field from host state.

        Returns:
            Every caller-visible physical identity field from host state.

        """
        return (
            state.st_dev,
            state.st_ino,
            state.st_nlink,
            getattr(state, "st_file_attributes", None),
            getattr(state, "st_reparse_tag", None),
        )

    @staticmethod
    def _planned_physical_state(state: m.Cli.AtomicFileState) -> PhysicalState:
        if state.device is None or state.inode is None or state.link_count is None:
            message = (
                f"existing atomic file state lacks physical identity: {state.path}"
            )
            raise OSError(errno.EINVAL, message, state.path)
        return (
            state.device,
            state.inode,
            state.link_count,
            state.file_attributes,
            state.reparse_tag,
        )


__all__: list[str] = ["FlextCliUtilitiesAtomicFileModel"]
