"""Descriptor-bound symbolic-link snapshots and exact preconditions."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from flext_cli import m

from . import atomic_file_descriptor as descriptor


def read_symlink_state(
    path: Path,
    parent: descriptor.ParentDescriptor,
    *,
    required: bool = False,
) -> m.Cli.AtomicSymlinkState:
    """Read link text through the same pinned parent as its lstat identity."""
    try:
        observed = descriptor.entry_stat(parent, path)
    except FileNotFoundError:
        if required:
            raise
        descriptor.assert_parent_unchanged(parent)
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
    after = descriptor.entry_stat(parent, path)
    if symlink_identity(observed) != symlink_identity(after):
        msg = f"atomic symlink changed during snapshot: {path}"
        raise OSError(errno.ESTALE, msg, path)
    descriptor.assert_parent_unchanged(parent)
    return m.Cli.AtomicSymlinkState(
        path=path,
        parent_device=parent.state.st_dev,
        parent_inode=parent.state.st_ino,
        target=target,
        identity=symlink_identity(observed),
    )


def symlink_identity(observed: os.stat_result) -> m.Cli.AtomicSymlinkIdentity:
    """Bind mutation-relevant identity without read-induced access time."""
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


def require_symlink_state(
    before: m.Cli.AtomicSymlinkState,
    parent: descriptor.ParentDescriptor,
) -> None:
    """Reject any parent, leaf identity or link-text drift before mutation."""
    if read_symlink_state(before.path, parent) != before:
        msg = f"atomic symlink changed after snapshot: {before.path}"
        raise OSError(errno.ESTALE, msg, before.path)


__all__: list[str] = ["read_symlink_state", "require_symlink_state", "symlink_identity"]
