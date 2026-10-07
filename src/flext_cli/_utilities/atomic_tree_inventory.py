"""Descriptor-authenticated inventory for one physical filesystem tree.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from typing import Literal, Never

from flext_cli import m, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicDirectoryState,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileState,
    FlextCliUtilitiesAtomicTreeDescriptor,
)


class FlextCliUtilitiesAtomicTreeInventory:
    """Canonical namespace owner."""

    _DIRECTORY_FLAGS = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )

    @staticmethod
    def inventory_physical_tree(root_path: Path) -> m.Cli.AtomicPhysicalTreeManifest:
        """Inventory one exact tree through non-aliased directory descriptors.

        Returns:
            The resulting ``m.Cli.AtomicPhysicalTreeManifest``.

        Raises:
            FileNotFoundError: If ``root_state is None``.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(root_path)
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(root_path)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            root_path,
        ) as outer_parent:
            parent_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                outer_parent.descriptor,
                outer_parent.path,
            )
            root_state = FlextCliUtilitiesAtomicDirectoryState.destination_state(
                root_path,
                parent=outer_parent,
            )
            if root_state is None:
                message = f"required atomic physical-tree root is missing: {root_path}"
                raise FileNotFoundError(errno.ENOENT, message, root_path)
            entries: list[m.Cli.AtomicPhysicalTreeEntry] = []
            with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                outer_parent,
                root_path,
                FlextCliUtilitiesAtomicTreeInventory._DIRECTORY_FLAGS,
            ) as descriptor:
                FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                    descriptor,
                    root_path,
                    root_state,
                )
                root_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                    descriptor,
                    root_path,
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                    root_path,
                    parent_mount_id,
                    root_mount_id,
                )
                root = FlextCliUtilitiesAtomicTreeInventory._entry(
                    root_path,
                    "directory",
                    outer_parent.state,
                    root_state,
                    parent_mount_id=parent_mount_id,
                    mount_id=root_mount_id,
                )
                root_parent = FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                    root_path,
                    descriptor,
                    root_state,
                    (
                        *outer_parent.ancestry,
                        FlextCliUtilitiesAtomicFilePath.identity(root_state),
                    ),
                    (*outer_parent.lineage, outer_parent.descriptor),
                )
                directory_identities = {
                    FlextCliUtilitiesAtomicFilePath.identity(root_state),
                }
                FlextCliUtilitiesAtomicTreeInventory._inventory_directory(
                    root_parent,
                    root_mount_id,
                    entries,
                    directory_identities,
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                    descriptor,
                    root_path,
                    root_state,
                )
            FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                outer_parent,
                root_path,
                root_state,
            )
        return m.Cli.AtomicPhysicalTreeManifest(
            root=root,
            entries=tuple(
                sorted(
                    entries,
                    key=FlextCliUtilitiesAtomicTreeInventory._entry_path_key,
                ),
            ),
        )

    @staticmethod
    def _inventory_directory(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        parent_mount_id: int,
        entries: list[m.Cli.AtomicPhysicalTreeEntry],
        directory_identities: set[t.Pair[int, int]],
    ) -> None:
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )
        names = FlextCliUtilitiesAtomicTreeInventory._directory_names(parent.descriptor)
        for name in names:
            path = parent.path / name
            observed = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
            if stat.S_ISDIR(observed.st_mode):
                FlextCliUtilitiesAtomicFilePath.validate_directory_state(path, observed)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    observed,
                )
                identity = FlextCliUtilitiesAtomicFilePath.identity(observed)
                if identity in directory_identities:
                    message = f"atomic physical-tree directory identity repeats: {path}"
                    raise OSError(errno.ELOOP, message, path)
                with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                    parent,
                    path,
                    FlextCliUtilitiesAtomicTreeInventory._DIRECTORY_FLAGS,
                ) as descriptor:
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                    mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                        descriptor,
                        path,
                    )
                    FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                        path,
                        parent_mount_id,
                        mount_id,
                    )
                    directory_identities.add(identity)
                    entries.append(
                        FlextCliUtilitiesAtomicTreeInventory._entry(
                            path,
                            "directory",
                            parent.state,
                            observed,
                            parent_mount_id=parent_mount_id,
                            mount_id=mount_id,
                        ),
                    )
                    child_parent = (
                        FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                            path,
                            descriptor,
                            observed,
                            (
                                *parent.ancestry,
                                FlextCliUtilitiesAtomicFilePath.identity(observed),
                            ),
                            (*parent.lineage, parent.descriptor),
                        )
                    )
                    FlextCliUtilitiesAtomicTreeInventory._inventory_directory(
                        child_parent,
                        mount_id,
                        entries,
                        directory_identities,
                    )
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent,
                    path,
                    observed,
                )
            elif stat.S_ISREG(observed.st_mode):
                authenticated = FlextCliUtilitiesAtomicFileState.destination_state(
                    path,
                    parent=parent,
                )
                if authenticated is None:
                    FlextCliUtilitiesAtomicTreeInventory._raise_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    authenticated,
                )
                size, digest = (
                    FlextCliUtilitiesAtomicTreeDescriptor.measure_authenticated_file(
                        parent,
                        path,
                        authenticated,
                        required_mount_id=parent_mount_id,
                    )
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreeInventory._entry(
                        path,
                        "file",
                        parent.state,
                        authenticated,
                        parent_mount_id=parent_mount_id,
                        size=size,
                        digest=digest,
                        mount_id=parent_mount_id,
                    ),
                )
            elif stat.S_ISLNK(observed.st_mode):
                target = os.readlink(name, dir_fd=parent.descriptor)
                if not target:
                    FlextCliUtilitiesAtomicTreeInventory._raise_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent,
                    path,
                    observed,
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    observed,
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreeInventory._entry(
                        path,
                        "symlink",
                        parent.state,
                        observed,
                        parent_mount_id=parent_mount_id,
                        mount_id=parent_mount_id,
                        link_target=target,
                    ),
                )
            else:
                message = (
                    f"atomic physical-tree entry is not regular or a directory: {path}"
                )
                raise OSError(errno.EINVAL, message, path)
        if (
            FlextCliUtilitiesAtomicTreeInventory._directory_names(parent.descriptor)
            != names
        ):
            FlextCliUtilitiesAtomicTreeInventory._raise_changed(parent.path)
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )

    @staticmethod
    def _entry(
        path: Path,
        kind: Literal["directory", "file", "symlink"],
        parent: os.stat_result,
        observed: os.stat_result,
        *,
        parent_mount_id: int,
        mount_id: int,
        size: int | None = None,
        digest: str | None = None,
        link_target: str | None = None,
    ) -> m.Cli.AtomicPhysicalTreeEntry:
        if kind == "file" and observed.st_nlink > 1:
            # Cleanup authority is per pathname; a second physical name sharing
            # the inode means pruning this tree must not silently claim the
            # sibling's content. Read/replace paths stay permissive — this
            # refusal owns the cleanup verb only.
            message = (
                f"cleanup authority refused: {path} has {observed.st_nlink} hard"
                " links (another physical name owns the same inode)"
            )
            raise OSError(errno.EMLINK, message, path)
        return m.Cli.AtomicPhysicalTreeEntry(
            path=path,
            kind=kind,
            parent_device=parent.st_dev,
            parent_inode=parent.st_ino,
            parent_mount_id=parent_mount_id,
            mode=stat.S_IMODE(observed.st_mode),
            device=observed.st_dev,
            inode=observed.st_ino,
            mount_id=mount_id,
            link_count=observed.st_nlink,
            uid=observed.st_uid,
            gid=observed.st_gid,
            mtime_ns=observed.st_mtime_ns,
            ctime_ns=observed.st_ctime_ns,
            file_attributes=getattr(observed, "st_file_attributes", None),
            reparse_tag=getattr(observed, "st_reparse_tag", None),
            size=size,
            sha256=digest,
            link_target=link_target,
        )

    @staticmethod
    def _directory_names(descriptor: int) -> t.VariadicTuple[str]:
        """Enumerate names through the authenticated directory descriptor.

        Returns:
            The resulting ``t.VariadicTuple[str]``.

        """
        with os.scandir(descriptor) as entries:
            return tuple(sorted(entry.name for entry in entries))

    @staticmethod
    def _entry_path_key(entry: m.Cli.AtomicPhysicalTreeEntry) -> str:
        """Return the deterministic lexical manifest key.

        Returns:
            The deterministic lexical manifest key.

        """
        return entry.path.as_posix()

    @staticmethod
    def _raise_changed(path: Path) -> Never:
        message = f"atomic physical-tree entry changed during inventory: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeInventory"]
