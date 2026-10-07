"""Guarded symbolic-link publication under a caller-held exclusive lease.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import uuid
from typing import TYPE_CHECKING

from flext_cli._utilities import FlextCliUtilitiesAtomicFileDescriptor

if TYPE_CHECKING:
    from pathlib import Path

    from flext_cli import m


class FlextCliUtilitiesAtomicSymlinkPublish:
    """Canonical namespace owner."""

    @staticmethod
    def _validated_target(path: Path, target: str) -> None:
        """Reject empty, NUL-containing, or non-UTF-8 publication targets.

        Raises:
            OSError: If ``os.symlink not in os.supports_dir_fd or os.readlink not in
                os.supports_dir_fd``.
            ValueError: If atomic symlink target must be nonempty and contain no NUL.

        """
        if not target or "\0" in target:
            msg = "atomic symlink target must be nonempty and contain no NUL"
            raise ValueError(msg)
        target.encode("utf-8", errors="strict")
        if (
            os.symlink not in os.supports_dir_fd
            or os.readlink not in os.supports_dir_fd
        ):
            msg = "descriptor-bound symbolic links are unsupported"
            raise OSError(errno.ENOTSUP, msg, path)

    @staticmethod
    def _stage_verified_link(
        before: m.Cli.AtomicSymlinkState,
        target: str,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
    ) -> tuple[Path, m.Cli.AtomicSymlinkState]:
        """Create the staged link and prove it still names the target.

        Returns:
            The resulting ``tuple[Path, m.Cli.AtomicSymlinkState]``.

        Raises:
            OSError: If ``observed.target != target``.

        """
        from flext_cli._utilities import FlextCliUtilitiesAtomicSymlinkState
        path = before.path
        staged_path = path.with_name(f".flext-symlink-{uuid.uuid4().hex}")
        os.symlink(target, staged_path.name, dir_fd=parent.descriptor)
        observed = FlextCliUtilitiesAtomicSymlinkState.read_symlink_state(
            staged_path,
            parent,
            required=True,
        )
        if observed.target != target:
            msg = f"staged symbolic link changed before publication: {staged_path}"
            raise OSError(errno.ESTALE, msg, staged_path)
        return staged_path, observed

    @staticmethod
    def _discard_staged(
        staged: m.Cli.AtomicSymlinkState,
        staged_path: Path,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
    ) -> None:
        """Remove one staged link that never published, authenticated first."""
        from flext_cli._utilities import FlextCliUtilitiesAtomicFileDurability, FlextCliUtilitiesAtomicSymlinkState
        FlextCliUtilitiesAtomicSymlinkState.require_symlink_state(staged, parent)
        FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, staged_path)
        FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)

    @staticmethod
    def _swap_staged_link(
        before: m.Cli.AtomicSymlinkState,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        staged_path: Path,
    ) -> None:
        """Swap the staged link into place under the caller-held lease."""
        from flext_cli._utilities import FlextCliUtilitiesAtomicDirectoryNoreplace, FlextCliUtilitiesAtomicFileDurability
        if before.target is None:
            FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
            FlextCliUtilitiesAtomicDirectoryNoreplace.rename_noreplace(
                parent.descriptor,
                staged_path.name,
                parent.descriptor,
                before.path.name,
                path=before.path,
            )
        else:
            FlextCliUtilitiesAtomicFileDescriptor.replace_entry(
                parent,
                staged_path,
                parent,
                before.path,
            )
        FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)

    @staticmethod
    def _verify_published(
        path: Path,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        target: str,
        staged: m.Cli.AtomicSymlinkState,
    ) -> None:
        """Prove the published link kept its target and its staged identity.

        Raises:
            OSError: If ``after.target != target or after.identity is None or
            staged.identity is None``; or if ``(after.identity.device,
            after.identity.inode) != (staged.identity.device, staged.identity.inode)``.

        """
        from flext_cli._utilities import FlextCliUtilitiesAtomicSymlinkState
        after = FlextCliUtilitiesAtomicSymlinkState.read_symlink_state(
            path,
            parent,
            required=True,
        )
        if after.target != target or after.identity is None or staged.identity is None:
            msg = f"atomic symlink publication did not retain its target: {path}"
            raise OSError(errno.ESTALE, msg, path)
        if (after.identity.device, after.identity.inode) != (
            staged.identity.device,
            staged.identity.inode,
        ):
            msg = f"atomic symlink publication changed inode: {path}"
            raise OSError(errno.ESTALE, msg, path)

    @staticmethod
    def write_guarded_symlink(before: m.Cli.AtomicSymlinkState, target: str) -> None:
        """Replace one authenticated link, or create at authenticated absence.

        All cooperative writers must hold the same lease from snapshot to effect.
        This is not compare-and-swap against actors that ignore that lease.

        Raises:
            BaseExceptionGroup: If symlink publication and staged cleanup failed.

        """
        from flext_cli._utilities import FlextCliUtilitiesAtomicDirectoryNoreplace, FlextCliUtilitiesAtomicSymlinkState
        path = before.path
        FlextCliUtilitiesAtomicSymlinkPublish._validated_target(path, target)
        if before.target is None:
            FlextCliUtilitiesAtomicDirectoryNoreplace.require_noreplace_capability(path)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            path,
            replace=True,
            unlink=True,
        ) as parent:
            FlextCliUtilitiesAtomicSymlinkState.require_symlink_state(before, parent)
            if before.target == target:
                return
            staged_path, staged = (
                FlextCliUtilitiesAtomicSymlinkPublish._stage_verified_link(
                    before,
                    target,
                    parent,
                )
            )
            swapped = False
            try:
                FlextCliUtilitiesAtomicSymlinkState.require_symlink_state(
                    before,
                    parent,
                )
                FlextCliUtilitiesAtomicSymlinkState.require_symlink_state(
                    staged,
                    parent,
                )
                FlextCliUtilitiesAtomicSymlinkPublish._swap_staged_link(
                    before,
                    parent,
                    staged_path,
                )
                swapped = True
                FlextCliUtilitiesAtomicSymlinkPublish._verify_published(
                    path,
                    parent,
                    target,
                    staged,
                )
            except BaseException as primary:
                try:
                    if not swapped:
                        FlextCliUtilitiesAtomicSymlinkPublish._discard_staged(
                            staged,
                            staged_path,
                            parent,
                        )
                except BaseException as cleanup_error:
                    msg = "symlink publication and staged cleanup failed"
                    raise BaseExceptionGroup(
                        msg,
                        [primary, cleanup_error],
                    ) from cleanup_error
                raise

    @staticmethod
    def delete_guarded_symlink(before: m.Cli.AtomicSymlinkState) -> None:
        """Delete exactly one authenticated link, never its target.

        Raises:
            FileNotFoundError: If ``before.target is None``.
            OSError: If ``snapshot.read_symlink_state(before.path, parent).target is not
                None``.

        """
        from flext_cli._utilities import FlextCliUtilitiesAtomicFileDurability, FlextCliUtilitiesAtomicSymlinkState
        if before.target is None:
            msg = f"cannot delete an absent symbolic link: {before.path}"
            raise FileNotFoundError(errno.ENOENT, msg, before.path)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            before.path,
            unlink=True,
        ) as parent:
            FlextCliUtilitiesAtomicSymlinkState.require_symlink_state(before, parent)
            FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, before.path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            if (
                FlextCliUtilitiesAtomicSymlinkState.read_symlink_state(
                    before.path,
                    parent,
                ).target
                is not None
            ):
                msg = f"atomic symlink remains after deletion: {before.path}"
                raise OSError(errno.ENOENT, msg, before.path)


__all__: list[str] = ["FlextCliUtilitiesAtomicSymlinkPublish"]
