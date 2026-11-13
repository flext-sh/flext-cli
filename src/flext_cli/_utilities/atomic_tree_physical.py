"""Descriptor-authenticated physical inventory of directories and trees.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Generator, Mapping, MutableMapping
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, Never

from flext_cli import m, p
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileRead,
    FlextCliUtilitiesAtomicFileState,
    FlextCliUtilitiesAtomicParentDescriptor,
    FlextCliUtilitiesAtomicParentFailure,
    FlextCliUtilitiesAtomicTreeDescriptor,
)


class FlextCliUtilitiesAtomicTreePhysical:
    """Inventory one physical directory or tree through retained descriptors."""

    _DIRECTORY_FLAGS = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )

    @classmethod
    def _observe_physical_directory(
        cls,
        observations: MutableMapping[Path, p.Cli.AtomicDirectoryInventory],
        root_path: Path,
    ) -> p.Cli.AtomicDirectoryInventory:
        """Return one boundary-scoped native observation of a physical directory.

        The first request inside a verification boundary takes the fresh native
        inventory; later requests for the same path in that boundary reuse that
        one observation. The store is owned by the caller and never outlives the
        boundary, so no receipt is replayed across boundaries.

        Returns:
            The boundary-scoped native observation of the directory.

        """
        observed = observations.get(root_path)
        if observed is None:
            observed = cls.inventory_physical_directory(root_path)
            observations[root_path] = observed
        return observed

    @staticmethod
    def inventory_physical_directory(root_path: Path) -> p.Cli.AtomicDirectoryInventory:
        """Capture immediate elections without descending or hashing child payloads.

        Returns:
            The inventory of the immediate child names with their
            authenticated kinds and version keys.

        """
        with FlextCliUtilitiesAtomicTreePhysical._opened_root(root_path) as (
            root,
            parent,
        ):
            names = FlextCliUtilitiesAtomicTreePhysical._directory_names(
                parent.descriptor
            )
            entries: list[p.Cli.AtomicDirectoryName] = []
            for name in names:
                path = root.path / name
                child = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
                kind: Literal["directory", "file", "symlink", "other"]
                if stat.S_ISDIR(child.st_mode):
                    kind = "directory"
                elif stat.S_ISREG(child.st_mode):
                    kind = "file"
                elif stat.S_ISLNK(child.st_mode):
                    kind = "symlink"
                else:
                    kind = "other"
                entries.append(
                    m.Cli.AtomicDirectoryName(
                        name=name,
                        kind=kind,
                        version_key=FlextCliUtilitiesAtomicFileRead.state_key(child),
                        link_target=os.readlink(name, dir_fd=parent.descriptor)
                        if kind == "symlink"
                        else None,
                    )
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent, path, child
                )
            if names != FlextCliUtilitiesAtomicTreePhysical._directory_names(
                parent.descriptor
            ):
                FlextCliUtilitiesAtomicTreePhysical._raise_inventory_changed(root.path)
        return m.Cli.AtomicDirectoryInventory.model_validate({
            "root": root,
            "entries": tuple(entries),
        })

    @staticmethod
    def inventory_physical_tree(
        root_path: Path,
        reference: p.Cli.AtomicPhysicalTreeManifest | None = None,
    ) -> p.Cli.AtomicPhysicalTreeManifest:
        """Inventory one exact tree through non-aliased directory descriptors.

        The shared root acquisition rejects a missing physical-tree root with
        ``FileNotFoundError`` before any descendant is read.

        A ``reference`` manifest is a previously proven inventory of the same
        tree. A regular file whose authenticated version identity (device,
        inode, size, mode, owner, link count, mtime and ctime, the same fields
        ``state_key`` treats as one file version) is unchanged keeps the digest
        the reference proved instead of being read again. Every other file, and
        every file absent from the reference, is hashed; the walk and all
        descriptor guards are unchanged.

        Returns:
            The resulting ``m.Cli.AtomicPhysicalTreeManifest``.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(root_path)
        entries: list[p.Cli.AtomicPhysicalTreeEntry] = []
        proven = (
            {
                root_path / entry.path.relative_to(reference.root.path): entry
                for entry in reference.entries
                if entry.kind == "file"
            }
            if reference is not None
            else {}
        )
        with FlextCliUtilitiesAtomicTreePhysical._opened_root(root_path) as (
            root,
            parent,
        ):
            FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                root.path, os.fstat(parent.lineage[-1]), parent.state
            )
            FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                root.path, root.parent_mount_id, root.mount_id
            )
            FlextCliUtilitiesAtomicTreePhysical._inventory_directory(
                parent, root.mount_id, entries, {(root.device, root.inode)}, proven
            )
        return m.Cli.AtomicPhysicalTreeManifest(
            root=root,
            entries=tuple(
                sorted(entries, key=FlextCliUtilitiesAtomicTreePhysical._entry_path_key)
            ),
        )

    @staticmethod
    @contextmanager
    def _opened_root(
        root_path: Path,
    ) -> Generator[
        tuple[
            p.Cli.AtomicPhysicalTreeEntry,
            FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        ]
    ]:
        """Retain one shared root acquisition for shallow and recursive inventories.

        Yields:
            The authenticated root entry and its retained parent descriptor
            for the duration of the inventory.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_directory_path(root_path)
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(root_path)
        with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
            root_path,
        ) as opened:
            parent_descriptor = (
                opened.lineage[-1] if opened.lineage else opened.descriptor
            )
            parent_state = os.fstat(parent_descriptor)
            parent_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.tree_mount_id(
                parent_descriptor,
                root_path.parent,
            )
            root_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.tree_mount_id(
                opened.descriptor,
                root_path,
            )
            root = FlextCliUtilitiesAtomicTreePhysical._entry(
                root_path,
                parent_state,
                opened.state,
                m.Cli.TreeEntryDetails(
                    kind="directory",
                    parent_mount_id=parent_mount_id,
                    mount_id=root_mount_id,
                ),
            )
            root_parent = FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                root_path,
                opened.descriptor,
                opened.state,
                opened.ancestry,
                opened.lineage,
            )

            def recheck() -> None:
                FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                    opened.descriptor,
                    root_path,
                    opened.state,
                )
                FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(
                    root_parent
                )

            try:
                yield root, root_parent
            except BaseException as exc:
                FlextCliUtilitiesAtomicParentFailure.preserve_recheck_failure(
                    root_path, exc, recheck
                )
                raise
            recheck()

    @staticmethod
    def _inventory_directory(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        parent_mount_id: int,
        entries: list[p.Cli.AtomicPhysicalTreeEntry],
        directory_identities: set[tuple[int, int]],
        proven: Mapping[Path, p.Cli.AtomicPhysicalTreeEntry],
    ) -> None:
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )
        names = FlextCliUtilitiesAtomicTreePhysical._directory_names(parent.descriptor)
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
                identity = FlextCliUtilitiesAtomicFilePath.path_identity(observed)
                if identity in directory_identities:
                    message = f"atomic physical-tree directory identity repeats: {path}"
                    raise OSError(errno.ELOOP, message, path)
                with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                    parent,
                    path,
                    FlextCliUtilitiesAtomicTreePhysical._DIRECTORY_FLAGS,
                ) as descriptor:
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                    mount_id = FlextCliUtilitiesAtomicTreeDescriptor.tree_mount_id(
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
                        FlextCliUtilitiesAtomicTreePhysical._entry(
                            path,
                            parent.state,
                            observed,
                            m.Cli.TreeEntryDetails(
                                kind="directory",
                                parent_mount_id=parent_mount_id,
                                mount_id=mount_id,
                            ),
                        ),
                    )
                    child_parent = (
                        FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                            path,
                            descriptor,
                            observed,
                            (
                                *parent.ancestry,
                                FlextCliUtilitiesAtomicFilePath.path_identity(observed),
                            ),
                            (*parent.lineage, parent.descriptor),
                        )
                    )
                    FlextCliUtilitiesAtomicTreePhysical._inventory_directory(
                        child_parent,
                        mount_id,
                        entries,
                        directory_identities,
                        proven,
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
                authenticated = FlextCliUtilitiesAtomicFileState.file_destination_state(
                    path,
                    parent=parent,
                )
                if authenticated is None:
                    FlextCliUtilitiesAtomicTreePhysical._raise_inventory_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    authenticated,
                )
                size, digest = FlextCliUtilitiesAtomicTreePhysical._file_digest(
                    parent,
                    path,
                    authenticated,
                    parent_mount_id,
                    proven.get(path),
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreePhysical._entry(
                        path,
                        parent.state,
                        authenticated,
                        m.Cli.TreeEntryDetails(
                            kind="file",
                            parent_mount_id=parent_mount_id,
                            size=size,
                            digest=digest,
                            mount_id=parent_mount_id,
                        ),
                    ),
                )
            elif stat.S_ISLNK(observed.st_mode):
                target = os.readlink(name, dir_fd=parent.descriptor)
                if not target:
                    FlextCliUtilitiesAtomicTreePhysical._raise_inventory_changed(path)
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
                    FlextCliUtilitiesAtomicTreePhysical._entry(
                        path,
                        parent.state,
                        observed,
                        m.Cli.TreeEntryDetails(
                            kind="symlink",
                            parent_mount_id=parent_mount_id,
                            mount_id=parent_mount_id,
                            link_target=target,
                        ),
                    ),
                )
            else:
                message = (
                    f"atomic physical-tree entry is not regular or a directory: {path}"
                )
                raise OSError(errno.EINVAL, message, path)
        if (
            FlextCliUtilitiesAtomicTreePhysical._directory_names(parent.descriptor)
            != names
        ):
            FlextCliUtilitiesAtomicTreePhysical._raise_inventory_changed(parent.path)
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )

    @staticmethod
    def _file_digest(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        authenticated: os.stat_result,
        mount_id: int,
        prior: p.Cli.AtomicPhysicalTreeEntry | None,
    ) -> tuple[int, str]:
        """Reuse a proven digest for an unchanged inode, or hash the file.

        Returns:
            The file size and SHA-256 digest.

        """
        if (
            prior is not None
            and prior.size is not None
            and prior.sha256 is not None
            and (
                prior.device,
                prior.inode,
                prior.size,
                prior.mode,
                prior.uid,
                prior.gid,
                prior.link_count,
                prior.mtime_ns,
                prior.ctime_ns,
            )
            == (
                authenticated.st_dev,
                authenticated.st_ino,
                authenticated.st_size,
                stat.S_IMODE(authenticated.st_mode),
                authenticated.st_uid,
                authenticated.st_gid,
                authenticated.st_nlink,
                authenticated.st_mtime_ns,
                authenticated.st_ctime_ns,
            )
        ):
            return prior.size, prior.sha256
        return FlextCliUtilitiesAtomicTreeDescriptor.measure_authenticated_file(
            parent,
            path,
            authenticated,
            required_mount_id=mount_id,
        )

    @staticmethod
    def _entry(
        path: Path,
        parent: os.stat_result,
        observed: os.stat_result,
        details: p.Cli.TreeEntryDetails,
    ) -> p.Cli.AtomicPhysicalTreeEntry:
        if details.kind == "file" and observed.st_nlink > 1:
            # Cleanup authority is per pathname; a second physical name sharing
            # the inode means pruning this tree must not silently claim the
            # sibling's content. Read/replace paths stay permissive — this
            # refusal owns the cleanup verb only.
            message = (
                f"cleanup authority refused: {path} has {observed.st_nlink} hard"
                " links (another physical name owns the same inode); "
                f"device={observed.st_dev} inode={observed.st_ino}"
            )
            raise OSError(errno.EMLINK, message, path)
        return m.Cli.AtomicPhysicalTreeEntry(
            path=path,
            kind=details.kind,
            parent_device=parent.st_dev,
            parent_inode=parent.st_ino,
            parent_mount_id=details.parent_mount_id,
            mode=stat.S_IMODE(observed.st_mode),
            device=observed.st_dev,
            inode=observed.st_ino,
            mount_id=details.mount_id,
            link_count=observed.st_nlink,
            uid=observed.st_uid,
            gid=observed.st_gid,
            mtime_ns=observed.st_mtime_ns,
            ctime_ns=observed.st_ctime_ns,
            file_attributes=getattr(observed, "st_file_attributes", None),
            reparse_tag=getattr(observed, "st_reparse_tag", None),
            size=details.size,
            sha256=details.digest,
            link_target=details.link_target,
        )

    @staticmethod
    def _directory_names(descriptor: int) -> tuple[str, ...]:
        """Enumerate names through the authenticated directory descriptor.

        Returns:
            The resulting ``tuple[str, ...],``.

        """
        with os.scandir(descriptor) as entries:
            return tuple(sorted(entry.name for entry in entries))

    @staticmethod
    def _entry_path_key(entry: p.Cli.AtomicPhysicalTreeEntry) -> str:
        """Return the deterministic lexical manifest key.

        Returns:
            The deterministic lexical manifest key.

        """
        return entry.path.as_posix()

    @staticmethod
    def _raise_inventory_changed(path: Path) -> Never:
        message = f"atomic physical-tree entry changed during inventory: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreePhysical"]
