"""Descriptor-bound symbolic-link snapshots and exact preconditions.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from flext_cli import m
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)


class FlextCliUtilitiesAtomicSymlinkState:
    """Canonical namespace owner."""

    @staticmethod
    def read_symlink_state(
        path: Path,
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        *,
        required: bool = False,
    ) -> m.Cli.AtomicSymlinkState:
        """Read link text through the same pinned parent as its lstat identity.

        Returns:
            The resulting ``m.Cli.AtomicSymlinkState``.

        Raises:
            FileNotFoundError: If ``required``.
            OSError: If ``not stat.S_ISLNK(observed.st_mode)``; or if
                ``symlink_identity(observed) != symlink_identity(after)``.

        """
        try:
            observed = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
        except FileNotFoundError:
            if required:
                raise
            FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
            return m.Cli.AtomicSymlinkState(
                path=path,
                parent_device=parent.state.st_dev,
                parent_inode=parent.state.st_ino,
                target=None,
                identity=None,
            )
        if not stat.S_ISLNK(observed.st_mode):
            msg = f"atomic symlink path is not a symbolic link: {path}"
            raise OSError(errno.EINVAL, msg, path)
        target = os.readlink(path.name, dir_fd=parent.descriptor)
        target.encode("utf-8", errors="strict")
        after = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
        if FlextCliUtilitiesAtomicSymlinkState.symlink_identity(
            observed,
        ) != FlextCliUtilitiesAtomicSymlinkState.symlink_identity(after):
            msg = f"atomic symlink changed during snapshot: {path}"
            raise OSError(errno.ESTALE, msg, path)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
        return m.Cli.AtomicSymlinkState(
            path=path,
            parent_device=parent.state.st_dev,
            parent_inode=parent.state.st_ino,
            target=target,
            identity=FlextCliUtilitiesAtomicSymlinkState.symlink_identity(observed),
        )

    @staticmethod
    def symlink_identity(observed: os.stat_result) -> m.Cli.AtomicSymlinkIdentity:
        """Bind mutation-relevant identity without read-induced access time.

        Returns:
            The resulting ``m.Cli.AtomicSymlinkIdentity``.

        """
        return m.Cli.AtomicSymlinkIdentity(
            mode=stat.S_IMODE(observed.st_mode),
            device=observed.st_dev,
            inode=observed.st_ino,
            link_count=observed.st_nlink,
            uid=observed.st_uid,
            gid=observed.st_gid,
            mtime_ns=observed.st_mtime_ns,
            ctime_ns=observed.st_ctime_ns,
            file_attributes=getattr(observed, "st_file_attributes", None),
            reparse_tag=getattr(observed, "st_reparse_tag", None),
        )

    @staticmethod
    def require_symlink_state(
        before: m.Cli.AtomicSymlinkState,
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
    ) -> None:
        """Reject any parent, leaf identity or link-text drift before mutation.

        Raises:
            OSError: If ``read_symlink_state(before.path, parent) != before``.

        """
        if (
            FlextCliUtilitiesAtomicSymlinkState.read_symlink_state(before.path, parent)
            != before
        ):
            msg = f"atomic symlink changed after snapshot: {before.path}"
            raise OSError(errno.ESTALE, msg, before.path)


__all__: list[str] = ["FlextCliUtilitiesAtomicSymlinkState"]
