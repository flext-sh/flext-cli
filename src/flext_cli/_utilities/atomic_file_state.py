"""Public filesystem-state authentication for the atomic publication owner.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from flext_cli import t
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead


class FlextCliUtilitiesAtomicFileState:
    """Canonical namespace owner."""

    @staticmethod
    def destination_state(
        path: Path,
        *,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor | None = None,
    ) -> os.stat_result | None:
        """Return an authorized destination snapshot without following links.

        Returns:
            An authorized destination snapshot without following links.

        """
        if parent is None:
            with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                path,
            ) as opened:
                state = FlextCliUtilitiesAtomicFileState.destination_state(
                    path,
                    parent=opened,
                )
                FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(opened)
                return state
        try:
            state = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
        except FileNotFoundError:
            state = None
        if state is None:
            return None
        FlextCliUtilitiesAtomicFileState._validate_regular_state(path, state)
        return state

    @staticmethod
    def validate_precondition(
        path: Path,
        state: os.stat_result | None,
        expected_bytes: bytes | None,
        *,
        enabled: bool,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor | None = None,
    ) -> None:
        """Authenticate an explicit raw-byte version before staging.

        Raises:
            FileExistsError: If ``state is not None``.
            FileNotFoundError: If ``state is None``.
            OSError: If ``read_authenticated_bytes(path, state, parent=parent) !=
                expected_bytes``.

        """
        if not enabled:
            return
        if expected_bytes is None:
            if state is not None:
                message = f"atomic destination exists but absence was required: {path}"
                raise FileExistsError(errno.EEXIST, message, path)
            return
        if state is None:
            message = f"atomic destination is missing: {path}"
            raise FileNotFoundError(errno.ENOENT, message, path)
        if (
            FlextCliUtilitiesAtomicFileState.read_authenticated_bytes(
                path,
                state,
                parent=parent,
            )
            != expected_bytes
        ):
            message = f"atomic destination content changed before write: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def assert_temporary_owned(
        temporary: Path,
        expected_identity: t.Pair[int, int],
        *,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor | None = None,
    ) -> None:
        """Require the staged pathname to retain its uniquely owned inode.

        Raises:
            FileNotFoundError: If a ``FileNotFoundError`` is caught.
            OSError: If ``identity(state) != expected_identity``.

        """
        if parent is None:
            with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                temporary,
            ) as opened:
                FlextCliUtilitiesAtomicFileState.assert_temporary_owned(
                    temporary,
                    expected_identity,
                    parent=opened,
                )
                return
        try:
            state = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, temporary)
        except FileNotFoundError as exc:
            message = f"atomic temporary disappeared before publication: {temporary}"
            raise FileNotFoundError(errno.ENOENT, message, temporary) from exc
        if FlextCliUtilitiesAtomicFileState.identity(state) != expected_identity:
            message = (
                f"atomic temporary identity changed before publication: {temporary}"
            )
            raise OSError(errno.ESTALE, message, temporary)
        FlextCliUtilitiesAtomicFileState._validate_regular_state(temporary, state)
        FlextCliUtilitiesAtomicFileState._validate_exclusive_link(temporary, state)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)

    @staticmethod
    def assert_destination_unchanged(
        path: Path,
        expected: os.stat_result | None,
        *,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor | None = None,
    ) -> None:
        """Fail before publication when destination identity or state changed.

        Raises:
            FileExistsError: If ``current is not None``.
            OSError: If ``current is None or file_read.state_key(current) !=
                file_read.state_key(expected)``.

        """
        if parent is None:
            with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                path,
            ) as opened:
                FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                    path,
                    expected,
                    parent=opened,
                )
                return
        current = FlextCliUtilitiesAtomicFileState.destination_state(
            path,
            parent=parent,
        )
        if expected is None:
            if current is not None:
                message = f"atomic destination appeared during write: {path}"
                raise FileExistsError(errno.EEXIST, message, path)
        elif current is None or FlextCliUtilitiesAtomicFileRead.state_key(
            current,
        ) != FlextCliUtilitiesAtomicFileRead.state_key(
            expected,
        ):
            message = f"atomic destination changed during write: {path}"
            raise OSError(errno.ESTALE, message, path)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)

    @staticmethod
    def identity(state: os.stat_result) -> t.Pair[int, int]:
        """Return the filesystem identity shared by descriptor and pathname stats.

        Returns:
            The filesystem identity shared by descriptor and pathname stats.

        """
        return FlextCliUtilitiesAtomicFilePath.identity(state)

    @staticmethod
    def read_authenticated_bytes(
        path: Path,
        expected: os.stat_result,
        *,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor | None = None,
    ) -> bytes:
        """Read exact bytes and prove the descriptor remains bound to its pathname.

        Returns:
            The resulting ``bytes``.

        """
        if parent is None:
            with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                path,
            ) as opened:
                return FlextCliUtilitiesAtomicFileState.read_authenticated_bytes(
                    path,
                    expected,
                    parent=opened,
                )
        content = FlextCliUtilitiesAtomicFileRead.read_descriptor_bytes(
            parent,
            path,
            expected,
        )
        FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
            path,
            expected,
            parent=parent,
        )
        return content

    @staticmethod
    def _validate_regular_state(path: Path, state: os.stat_result) -> None:
        if not stat.S_ISREG(
            state.st_mode,
        ) or FlextCliUtilitiesAtomicFilePath.is_reparse_point(state):
            message = f"atomic destination is not a regular file: {path}"
            raise OSError(errno.EINVAL, message, path)

    @staticmethod
    def _validate_exclusive_link(path: Path, state: os.stat_result) -> None:
        """Require exactly one pathname link for staged inode exclusivity.

        Publication swaps the destination entry, so destinations hardlinked by
        package managers (uv ``link-mode = clone``) are safe to replace; the
        staged temporary, however, must be uniquely owned or the descriptor-bound
        identity proof cannot distinguish the staged bytes from a sibling link.

        Raises:
            OSError: If ``state.st_nlink != 1``.

        """
        if state.st_nlink != 1:
            message = f"atomic staged file has {state.st_nlink} hard links: {path}"
            raise OSError(errno.EMLINK, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileState"]
