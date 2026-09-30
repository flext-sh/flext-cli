"""Guarded symbolic-link publication under a caller-held exclusive lease."""

from __future__ import annotations

import errno
import os
import sys
import uuid

from flext_cli import m

from . import (
    atomic_directory_noreplace as noreplace,
    atomic_file_descriptor as descriptor,
    atomic_file_durability as durability,
    atomic_symlink_state as snapshot,
)


def write_guarded_symlink(before: m.Cli.AtomicSymlinkState, target: str) -> None:
    """Replace one authenticated link, or create at authenticated absence.

    All cooperative writers must hold the same lease from snapshot to effect.
    This is not compare-and-swap against actors that ignore that lease.
    """
    path = before.path
    if not target or "\0" in target:
        msg = "atomic symlink target must be nonempty and contain no NUL"
        raise ValueError(msg)
    target.encode("utf-8", errors="strict")
    if os.symlink not in os.supports_dir_fd or os.readlink not in os.supports_dir_fd:
        msg = "descriptor-bound symbolic links are unsupported"
        raise OSError(errno.ENOTSUP, msg, path)
    if before.target is None:
        noreplace.require_noreplace_capability(path)
    with descriptor.parent_descriptor(path, replace=True, unlink=True) as parent:
        snapshot.require_symlink_state(before, parent)
        if before.target == target:
            return
        staged_path = path.with_name(f".flext-symlink-{uuid.uuid4().hex}")
        os.symlink(target, staged_path.name, dir_fd=parent.descriptor)
        staged: m.Cli.AtomicSymlinkState | None = None
        published = False
        try:
            observed = snapshot.read_symlink_state(staged_path, parent, required=True)
            if observed.target != target:
                msg = f"staged symbolic link changed before publication: {staged_path}"
                raise OSError(errno.ESTALE, msg, staged_path)
            staged = observed
            snapshot.require_symlink_state(before, parent)
            snapshot.require_symlink_state(staged, parent)
            if before.target is None:
                descriptor.assert_parent_unchanged(parent)
                noreplace.rename_noreplace(
                    parent.descriptor,
                    staged_path.name,
                    parent.descriptor,
                    path.name,
                    path=path,
                )
            else:
                descriptor.replace_entry(parent, staged_path, parent, path)
            published = True
            durability.sync_parent(parent)
            after = snapshot.read_symlink_state(path, parent, required=True)
            if (
                after.target != target
                or after.identity is None
                or staged.identity is None
            ):
                msg = f"atomic symlink publication did not retain its target: {path}"
                raise OSError(errno.ESTALE, msg, path)
            if (after.identity.device, after.identity.inode) != (
                staged.identity.device,
                staged.identity.inode,
            ):
                msg = f"atomic symlink publication changed inode: {path}"
                raise OSError(errno.ESTALE, msg, path)
        finally:
            if not published and staged is not None:
                primary = sys.exception()
                try:
                    snapshot.require_symlink_state(staged, parent)
                    descriptor.unlink_entry(parent, staged_path)
                    durability.sync_parent(parent)
                except BaseException as cleanup_error:
                    if primary is not None:
                        msg_0 = "symlink publication and staged cleanup failed"
                        raise BaseExceptionGroup(
                            msg_0, [primary, cleanup_error]
                        ) from primary
                    raise


def delete_guarded_symlink(before: m.Cli.AtomicSymlinkState) -> None:
    """Delete exactly one authenticated link, never its target."""
    if before.target is None:
        msg = f"cannot delete an absent symbolic link: {before.path}"
        raise FileNotFoundError(errno.ENOENT, msg, before.path)
    with descriptor.parent_descriptor(before.path, unlink=True) as parent:
        snapshot.require_symlink_state(before, parent)
        descriptor.unlink_entry(parent, before.path)
        durability.sync_parent(parent)
        if snapshot.read_symlink_state(before.path, parent).target is not None:
            msg = f"atomic symlink remains after deletion: {before.path}"
            raise OSError(errno.ESTALE, msg, before.path)


__all__: list[str] = ["delete_guarded_symlink", "write_guarded_symlink"]
