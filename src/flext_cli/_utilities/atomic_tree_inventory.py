"""Descriptor-authenticated inventory for one physical filesystem tree."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from typing import Literal, Never

from flext_cli import m

from . import atomic_directory_descriptor as directory_descriptor
from . import atomic_directory_state as directory_state
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_path as file_path
from . import atomic_file_state as file_state
from . import atomic_tree_descriptor as tree_descriptor

_DIRECTORY_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_BINARY", 0)
)


def inventory_physical_tree(root_path: Path) -> m.Cli.AtomicPhysicalTreeManifest:
    """Inventory one exact tree through non-aliased directory descriptors."""
    root_path = file_path.validate_atomic_path(root_path)
    directory_descriptor.require_read_capabilities(root_path)
    with file_descriptor.parent_descriptor(root_path) as outer_parent:
        parent_mount_id = tree_descriptor.mount_id(
            outer_parent.descriptor, outer_parent.path
        )
        root_state = directory_state.destination_state(root_path, parent=outer_parent)
        if root_state is None:
            message = f"required atomic physical-tree root is missing: {root_path}"
            raise FileNotFoundError(errno.ENOENT, message, root_path)
        entries: list[m.Cli.AtomicPhysicalTreeEntry] = []
        with file_descriptor.entry_descriptor(
            outer_parent, root_path, _DIRECTORY_FLAGS
        ) as descriptor:
            tree_descriptor.require_directory_state(descriptor, root_path, root_state)
            root_mount_id = tree_descriptor.mount_id(descriptor, root_path)
            tree_descriptor.require_mount(root_path, parent_mount_id, root_mount_id)
            root = _entry(
                root_path,
                "directory",
                outer_parent.state,
                root_state,
                parent_mount_id=parent_mount_id,
                mount_id=root_mount_id,
            )
            root_parent = file_descriptor.ParentDescriptor(
                root_path,
                descriptor,
                root_state,
                (*outer_parent.ancestry, file_path.identity(root_state)),
            )
            directory_identities = {file_path.identity(root_state)}
            _inventory_directory(
                root_parent, root_mount_id, entries, directory_identities
            )
            tree_descriptor.require_directory_state(descriptor, root_path, root_state)
        tree_descriptor.require_entry_state(outer_parent, root_path, root_state)
    return m.Cli.AtomicPhysicalTreeManifest(
        root=root, entries=tuple(sorted(entries, key=_entry_path_key))
    )


def _inventory_directory(
    parent: file_descriptor.ParentDescriptor,
    parent_mount_id: int,
    entries: list[m.Cli.AtomicPhysicalTreeEntry],
    directory_identities: set[tuple[int, int]],
) -> None:
    tree_descriptor.require_directory_state(
        parent.descriptor, parent.path, parent.state
    )
    names = _directory_names(parent.descriptor)
    for name in names:
        path = parent.path / name
        observed = file_descriptor.entry_stat(parent, path)
        if stat.S_ISDIR(observed.st_mode):
            file_path.validate_directory_state(path, observed)
            tree_descriptor.require_same_device(path, parent.state, observed)
            identity = file_path.identity(observed)
            if identity in directory_identities:
                message = f"atomic physical-tree directory identity repeats: {path}"
                raise OSError(errno.ELOOP, message, path)
            with file_descriptor.entry_descriptor(
                parent, path, _DIRECTORY_FLAGS
            ) as descriptor:
                tree_descriptor.require_directory_state(descriptor, path, observed)
                mount_id = tree_descriptor.mount_id(descriptor, path)
                tree_descriptor.require_mount(path, parent_mount_id, mount_id)
                directory_identities.add(identity)
                entries.append(
                    _entry(
                        path,
                        "directory",
                        parent.state,
                        observed,
                        parent_mount_id=parent_mount_id,
                        mount_id=mount_id,
                    )
                )
                child_parent = file_descriptor.ParentDescriptor(
                    path,
                    descriptor,
                    observed,
                    (*parent.ancestry, file_path.identity(observed)),
                )
                _inventory_directory(
                    child_parent, mount_id, entries, directory_identities
                )
                tree_descriptor.require_directory_state(descriptor, path, observed)
            tree_descriptor.require_entry_state(parent, path, observed)
        elif stat.S_ISREG(observed.st_mode):
            authenticated = file_state.destination_state(path, parent=parent)
            if authenticated is None:
                _raise_changed(path)
            tree_descriptor.require_same_device(path, parent.state, authenticated)
            size, digest = tree_descriptor.measure_authenticated_file(
                parent, path, authenticated, required_mount_id=parent_mount_id
            )
            entries.append(
                _entry(
                    path,
                    "file",
                    parent.state,
                    authenticated,
                    parent_mount_id=parent_mount_id,
                    size=size,
                    digest=digest,
                    mount_id=parent_mount_id,
                )
            )
        elif stat.S_ISLNK(observed.st_mode):
            target = os.readlink(name, dir_fd=parent.descriptor)
            if not target:
                _raise_changed(path)
            tree_descriptor.require_entry_state(parent, path, observed)
            tree_descriptor.require_same_device(path, parent.state, observed)
            entries.append(
                _entry(
                    path,
                    "symlink",
                    parent.state,
                    observed,
                    parent_mount_id=parent_mount_id,
                    mount_id=parent_mount_id,
                    link_target=target,
                )
            )
        else:
            message = (
                f"atomic physical-tree entry is not regular or a directory: {path}"
            )
            raise OSError(errno.EINVAL, message, path)
    if _directory_names(parent.descriptor) != names:
        _raise_changed(parent.path)
    tree_descriptor.require_directory_state(
        parent.descriptor, parent.path, parent.state
    )


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


def _directory_names(descriptor: int) -> tuple[str, ...]:
    """Enumerate names through the authenticated directory descriptor."""
    with os.scandir(descriptor) as entries:
        return tuple(sorted(entry.name for entry in entries))


def _entry_path_key(entry: m.Cli.AtomicPhysicalTreeEntry) -> str:
    """Return the deterministic lexical manifest key."""
    return entry.path.as_posix()


def _raise_changed(path: Path) -> Never:
    message = f"atomic physical-tree entry changed during inventory: {path}"
    raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["inventory_physical_tree"]
