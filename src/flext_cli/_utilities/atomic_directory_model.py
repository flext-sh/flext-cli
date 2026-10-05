"""Typed physical-state contracts for guarded empty-directory operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from flext_cli import m

type DirectoryPhysicalState = tuple[int, int, int, int, int | None, int | None]


class FlextCliUtilitiesAtomicDirectoryModel:
    """Canonical namespace owner."""

    @staticmethod
    def from_observed(
        path: Path,
        parent: os.stat_result | None,
        observed: os.stat_result | None,
    ) -> m.Cli.AtomicDirectoryState:
        """Build the caller-owned state from one authenticated observation.

        Returns:
            The resulting ``m.Cli.AtomicDirectoryState``.

        """
        return m.Cli.AtomicDirectoryState(
            path=path,
            exists=observed is not None,
            parent_device=None if parent is None else parent.st_dev,
            parent_inode=None if parent is None else parent.st_ino,
            mode=None if observed is None else stat.S_IMODE(observed.st_mode),
            device=None if observed is None else observed.st_dev,
            inode=None if observed is None else observed.st_ino,
            link_count=None if observed is None else observed.st_nlink,
            file_attributes=(
                None
                if observed is None
                else getattr(observed, "st_file_attributes", None)
            ),
            reparse_tag=(
                None if observed is None else getattr(observed, "st_reparse_tag", None)
            ),
        )

    @staticmethod
    def require_absent(state: m.Cli.AtomicDirectoryState, *, purpose: str) -> None:
        """Require the caller state to authorize creation from exact absence.

        Raises:
            FileExistsError: If ``state.exists``.

        """
        if state.exists:
            message = f"{purpose} atomic directory state already exists: {state.path}"
            raise FileExistsError(errno.EEXIST, message, state.path)

    @staticmethod
    def require_existing(state: m.Cli.AtomicDirectoryState, *, purpose: str) -> None:
        """Require the caller state to authorize an existing empty directory.

        Raises:
            FileNotFoundError: If ``not state.exists``.

        """
        if not state.exists:
            message = f"{purpose} atomic directory state is absent: {state.path}"
            raise FileNotFoundError(errno.ENOENT, message, state.path)

    @staticmethod
    def require_observed(
        planned: m.Cli.AtomicDirectoryState,
        observed: os.stat_result | None,
    ) -> None:
        """Require presence, mode, and every physical field to match the snapshot.

        Raises:
            OSError: If ``observed is None``; or if ``_planned_state(planned) !=
                physical_state(observed)``; or if ``observed is not None``.

        """
        if not planned.exists:
            if observed is not None:
                message = (
                    f"atomic directory appeared after absent snapshot: {planned.path}"
                )
                raise OSError(errno.ESTALE, message, planned.path)
            return
        if observed is None:
            message = f"atomic directory disappeared after snapshot: {planned.path}"
            raise OSError(errno.ESTALE, message, planned.path)
        if FlextCliUtilitiesAtomicDirectoryModel._planned_state(
            planned,
        ) != FlextCliUtilitiesAtomicDirectoryModel.physical_state(observed):
            message = f"atomic directory physical state changed: {planned.path}"
            raise OSError(errno.ESTALE, message, planned.path)

    @staticmethod
    def require_parent(
        planned: m.Cli.AtomicDirectoryState,
        observed: os.stat_result,
    ) -> None:
        """Require the authenticated parent to equal the snapshot parent identity.

        Raises:
            FileNotFoundError: If ``planned.parent_device is None or
            planned.parent_inode is None``. OSError: If ``(planned.parent_device,
            planned.parent_inode) != (observed.st_dev, observed.st_ino)``.
            OSError: If ``(planned.parent_device, planned.parent_inode) != (observed.st_dev,
                observed.st_ino)``.
        """
        if planned.parent_device is None or planned.parent_inode is None:
            message = (
                f"atomic directory parent was absent at snapshot: {planned.path.parent}"
            )
            raise FileNotFoundError(errno.ENOENT, message, planned.path.parent)
        if (planned.parent_device, planned.parent_inode) != (
            observed.st_dev,
            observed.st_ino,
        ):
            message = f"atomic directory parent identity changed: {planned.path.parent}"
            raise OSError(errno.ESTALE, message, planned.path.parent)

    @staticmethod
    def physical_state(state: os.stat_result) -> DirectoryPhysicalState:
        """Return every caller-visible directory identity field.

        Returns:
            Every caller-visible directory identity field.

        """
        return (
            stat.S_IMODE(state.st_mode),
            state.st_dev,
            state.st_ino,
            state.st_nlink,
            getattr(state, "st_file_attributes", None),
            getattr(state, "st_reparse_tag", None),
        )

    @staticmethod
    def _planned_state(state: m.Cli.AtomicDirectoryState) -> DirectoryPhysicalState:
        mode, device, inode, link_count = (
            state.mode,
            state.device,
            state.inode,
            state.link_count,
        )
        if mode is None or device is None or inode is None or link_count is None:
            message = f"existing atomic directory lacks physical identity: {state.path}"
            raise OSError(errno.EINVAL, message, state.path)
        return (
            mode,
            device,
            inode,
            link_count,
            state.file_attributes,
            state.reparse_tag,
        )


__all__: list[str] = ["DirectoryPhysicalState", "FlextCliUtilitiesAtomicDirectoryModel"]
