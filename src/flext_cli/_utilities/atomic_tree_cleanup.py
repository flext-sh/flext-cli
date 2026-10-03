"""Guarded exact-manifest cleanup for one physical filesystem tree.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from typing import Never

from flext_cli import m, t
from flext_cli._utilities.atomic_directory_delete import (
    FlextCliUtilitiesAtomicDirectoryDelete,
)
from flext_cli._utilities.atomic_directory_descriptor import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
)
from flext_cli._utilities.atomic_directory_snapshot import (
    FlextCliUtilitiesAtomicDirectorySnapshot,
)
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_durability import (
    FlextCliUtilitiesAtomicFileDurability,
)
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState
from flext_cli._utilities.atomic_parent_descriptor import (
    FlextCliUtilitiesAtomicParentDescriptor,
)
from flext_cli._utilities.atomic_tree_descriptor import (
    FlextCliUtilitiesAtomicTreeDescriptor,
)
from flext_cli._utilities.atomic_tree_inventory import (
    FlextCliUtilitiesAtomicTreeInventory,
)


class FlextCliUtilitiesAtomicTreeCleanup:
    """Canonical namespace owner."""

    @staticmethod
    def cleanup_physical_tree_guarded(
        manifest: m.Cli.AtomicPhysicalTreeManifest,
    ) -> None:
        """Delete only the exact manifested tree under the caller's exclusive lock."""
        FlextCliUtilitiesAtomicTreeCleanup._require_cleanup_capabilities(manifest)
        current = FlextCliUtilitiesAtomicTreeInventory.inventory_physical_tree(
            manifest.root.path
        )
        if current != manifest:
            FlextCliUtilitiesAtomicTreeCleanup._raise_changed(manifest.root.path)
        files = (entry for entry in manifest.entries if entry.kind == "file")
        for entry in sorted(
            files, key=FlextCliUtilitiesAtomicTreeCleanup._deletion_key, reverse=True
        ):
            FlextCliUtilitiesAtomicTreeCleanup._delete_file(entry)
        symlinks = (entry for entry in manifest.entries if entry.kind == "symlink")
        for entry in sorted(
            symlinks, key=FlextCliUtilitiesAtomicTreeCleanup._deletion_key, reverse=True
        ):
            FlextCliUtilitiesAtomicTreeCleanup._delete_symlink(entry)
        directories = [entry for entry in manifest.entries if entry.kind == "directory"]
        directories.append(manifest.root)
        for entry in sorted(
            directories,
            key=FlextCliUtilitiesAtomicTreeCleanup._deletion_key,
            reverse=True,
        ):
            FlextCliUtilitiesAtomicTreeCleanup._delete_directory(entry)

    @staticmethod
    def _require_cleanup_capabilities(
        manifest: m.Cli.AtomicPhysicalTreeManifest,
    ) -> None:
        root = manifest.root
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_delete_capabilities(
            root.path
        )
        FlextCliUtilitiesAtomicParentDescriptor.require_traversal_capabilities(
            root.path
        )
        if os.unlink not in os.supports_dir_fd:
            message = "descriptor-bound physical-tree file deletion is unsupported"
            raise OSError(errno.ENOTSUP, message, root.path)
        if not hasattr(os, "fsync"):
            message = "physical-tree cleanup durability sync is unsupported"
            raise OSError(errno.ENOTSUP, message, root.path)
        bindings: dict[Path, tuple[int, int, int]] = {}
        for entry in (root, *manifest.entries):
            expected = (entry.parent_device, entry.parent_inode, entry.parent_mount_id)
            prior = bindings.setdefault(entry.path.parent, expected)
            if prior != expected:
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path.parent)
        for path, expected in sorted(
            bindings.items(), key=FlextCliUtilitiesAtomicTreeCleanup._binding_path_key
        ):
            with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
                path
            ) as opened:
                mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                    opened.descriptor, path
                )
                if (opened.state.st_dev, opened.state.st_ino, mount_id) != expected:
                    FlextCliUtilitiesAtomicTreeCleanup._raise_changed(path)
                authenticated = (
                    FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor(
                        path,
                        opened.descriptor,
                        opened.state,
                        opened.ancestry,
                        opened.lineage,
                    )
                )
                FlextCliUtilitiesAtomicFileDurability.sync_parent(authenticated)

    @staticmethod
    def _delete_file(entry: m.Cli.AtomicPhysicalTreeEntry) -> None:
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            entry.path, unlink=True
        ) as parent:
            FlextCliUtilitiesAtomicTreeCleanup._require_parent(
                entry, parent.state.st_dev, parent.state.st_ino
            )
            parent_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                parent.descriptor, parent.path
            )
            if parent_mount_id != entry.parent_mount_id:
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(parent.path)
            observed = FlextCliUtilitiesAtomicFileState.destination_state(
                entry.path, parent=parent
            )
            if observed is None:
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)
            FlextCliUtilitiesAtomicTreeCleanup._require_file_state(entry, observed)
            size, digest = (
                FlextCliUtilitiesAtomicTreeDescriptor.measure_authenticated_file(
                    parent,
                    entry.path,
                    observed,
                    required_mount_id=entry.mount_id,
                )
            )
            if (size, digest) != (entry.size, entry.sha256):
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)
            FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                entry.path, observed, parent=parent
            )
            FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, entry.path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            if (
                FlextCliUtilitiesAtomicFileState.destination_state(
                    entry.path, parent=parent
                )
                is not None
            ):
                message = (
                    f"atomic physical-tree file still exists after delete: {entry.path}"
                )
                raise OSError(errno.ESTALE, message, entry.path)

    @staticmethod
    def _delete_symlink(entry: m.Cli.AtomicPhysicalTreeEntry) -> None:
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            entry.path, unlink=True
        ) as parent:
            FlextCliUtilitiesAtomicTreeCleanup._require_parent(
                entry, parent.state.st_dev, parent.state.st_ino
            )
            parent_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                parent.descriptor, parent.path
            )
            if parent_mount_id != entry.parent_mount_id:
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(parent.path)
            observed = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(
                parent, entry.path
            )
            if not stat.S_ISLNK(observed.st_mode):
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)
            if (
                stat.S_IMODE(observed.st_mode),
                observed.st_dev,
                observed.st_ino,
                observed.st_nlink,
                observed.st_uid,
                observed.st_gid,
                observed.st_mtime_ns,
                observed.st_ctime_ns,
                getattr(observed, "st_file_attributes", None),
                getattr(observed, "st_reparse_tag", None),
                os.readlink(entry.path.name, dir_fd=parent.descriptor),
            ) != (
                entry.mode,
                entry.device,
                entry.inode,
                entry.link_count,
                entry.uid,
                entry.gid,
                entry.mtime_ns,
                entry.ctime_ns,
                entry.file_attributes,
                entry.reparse_tag,
                entry.link_target,
            ):
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)
            FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, entry.path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            deletion_confirmed = False
            try:
                FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, entry.path)
            except FileNotFoundError:
                deletion_confirmed = True
            if not deletion_confirmed:
                FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)

    @staticmethod
    def _delete_directory(entry: m.Cli.AtomicPhysicalTreeEntry) -> None:
        current = (
            FlextCliUtilitiesAtomicDirectorySnapshot.read_authenticated_empty_directory(
                entry.path,
                required=True,
            )
        )
        if (
            not current.exists
            or current.mode is None
            or current.device is None
            or current.inode is None
        ):
            FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)
        FlextCliUtilitiesAtomicTreeCleanup._require_parent(
            entry, current.parent_device, current.parent_inode
        )
        if (
            current.mode,
            current.device,
            current.inode,
            current.file_attributes,
            current.reparse_tag,
        ) != (
            entry.mode,
            entry.device,
            entry.inode,
            entry.file_attributes,
            entry.reparse_tag,
        ):
            FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)
        FlextCliUtilitiesAtomicDirectoryDelete.remove_guarded_empty_directory(current)

    @staticmethod
    def _require_file_state(
        entry: m.Cli.AtomicPhysicalTreeEntry,
        observed: os.stat_result,
    ) -> None:
        if (
            stat.S_IMODE(observed.st_mode),
            observed.st_dev,
            observed.st_ino,
            observed.st_nlink,
            observed.st_uid,
            observed.st_gid,
            observed.st_mtime_ns,
            observed.st_ctime_ns,
            getattr(observed, "st_file_attributes", None),
            getattr(observed, "st_reparse_tag", None),
            observed.st_size,
        ) != (
            entry.mode,
            entry.device,
            entry.inode,
            entry.link_count,
            entry.uid,
            entry.gid,
            entry.mtime_ns,
            entry.ctime_ns,
            entry.file_attributes,
            entry.reparse_tag,
            entry.size,
        ):
            FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path)

    @staticmethod
    def _require_parent(
        entry: m.Cli.AtomicPhysicalTreeEntry,
        device: int | None,
        inode: int | None,
    ) -> None:
        if (entry.parent_device, entry.parent_inode) != (device, inode):
            FlextCliUtilitiesAtomicTreeCleanup._raise_changed(entry.path.parent)

    @staticmethod
    def _deletion_key(entry: m.Cli.AtomicPhysicalTreeEntry) -> t.Pair[int, str]:
        return (len(entry.path.parts), entry.path.as_posix())

    @staticmethod
    def _binding_path_key(item: t.Pair[Path, t.Triple[int, int, int]]) -> str:
        """Return the lexical key for one authenticated parent binding.

        Returns:
            The lexical key for one authenticated parent binding.

        """
        return item[0].as_posix()

    @staticmethod
    def _raise_changed(path: Path) -> Never:
        message = f"atomic physical-tree changed after manifest: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeCleanup"]
