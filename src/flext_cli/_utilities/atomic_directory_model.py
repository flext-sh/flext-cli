"""Typed physical-state contracts for guarded empty-directory operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from flext_cli import m, p
from flext_cli._utilities import FlextCliUtilitiesAtomicFileModel
from flext_cli.typings import DirectoryPhysicalState


class FlextCliUtilitiesAtomicDirectoryModel:
    """Canonical namespace owner."""

    @staticmethod
    def from_observed(
        path: Path,
        parent: os.stat_result | None,
        observed: os.stat_result | None,
    ) -> p.Cli.AtomicDirectoryState:
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
    def require_absent(state: p.Cli.AtomicDirectoryState, *, purpose: str) -> None:
        """Require the caller state to authorize creation from exact absence.

        Raises:
            FileExistsError: If ``state.exists``.

        """
        if state.exists:
            message = f"{purpose} atomic directory state already exists: {state.path}"
            raise FileExistsError(errno.EEXIST, message, state.path)

    @staticmethod
    def require_directory_existing(
        state: p.Cli.AtomicDirectoryState, *, purpose: str
    ) -> None:
        """Require the caller state to authorize an existing empty directory.

        Raises:
            FileNotFoundError: If ``not state.exists``.

        """
        if not state.exists:
            message = f"{purpose} atomic directory state is absent: {state.path}"
            raise FileNotFoundError(errno.ENOENT, message, state.path)

    @staticmethod
    def require_directory_observed(
        planned: p.Cli.AtomicDirectoryState,
        observed: os.stat_result | None,
    ) -> None:
        """Require presence, mode, and every physical field to match the snapshot.

        Raises:
            OSError: If the presence or physical state changed after the snapshot.

        """
        current = FlextCliUtilitiesAtomicFileModel.require_snapshot_presence(
            planned.path, observed, present=planned.exists, subject="directory"
        )
        if current is not None and FlextCliUtilitiesAtomicDirectoryModel._planned_state(
            planned,
        ) != FlextCliUtilitiesAtomicDirectoryModel.directory_physical_state(current):
            message = f"atomic directory physical state changed: {planned.path}"
            raise OSError(errno.ESTALE, message, planned.path)

    @staticmethod
    def directory_physical_state(state: os.stat_result) -> DirectoryPhysicalState:
        """Return every caller-visible directory identity field.

        Returns:
            Every caller-visible directory identity field.

        """
        return (
            stat.S_IMODE(state.st_mode),
            *FlextCliUtilitiesAtomicFileModel.physical_state(state),
        )

    @staticmethod
    def _planned_state(state: p.Cli.AtomicDirectoryState) -> DirectoryPhysicalState:
        if state.mode is None:
            message = f"existing atomic directory lacks physical identity: {state.path}"
            raise OSError(errno.EINVAL, message, state.path)
        return (
            state.mode,
            *FlextCliUtilitiesAtomicFileModel.planned_physical_state(
                state, subject="directory"
            ),
        )


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryModel"]
