"""Guarded exact-manifest cleanup for one physical filesystem tree."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from typing import Never

from flext_cli import m

from . import atomic_directory_delete as directory_delete
from . import atomic_directory_descriptor as directory_descriptor
from . import atomic_directory_snapshot as directory_snapshot
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_durability as file_durability
from . import atomic_file_state as file_state
from . import atomic_parent_descriptor as parent_descriptor
from . import atomic_tree_descriptor as tree_descriptor
from . import atomic_tree_inventory as tree_inventory


def cleanup_physical_tree_guarded(
    manifest: m.Cli.AtomicPhysicalTreeManifest,
) -> None:
    """Delete only the exact manifested tree under the caller's exclusive lock."""
    _require_cleanup_capabilities(manifest)
    current = tree_inventory.inventory_physical_tree(manifest.root.path)
    if current != manifest:
        _raise_changed(manifest.root.path)
    files = (entry for entry in manifest.entries if entry.kind == "file")
    for entry in sorted(files, key=_deletion_key, reverse=True):
        _delete_file(entry)
    directories = [
        entry for entry in manifest.entries if entry.kind == "directory"
    ]
    directories.append(manifest.root)
    for entry in sorted(directories, key=_deletion_key, reverse=True):
        _delete_directory(entry)


def _require_cleanup_capabilities(
    manifest: m.Cli.AtomicPhysicalTreeManifest,
) -> None:
    root = manifest.root
    directory_descriptor.require_delete_capabilities(root.path)
    parent_descriptor.require_traversal_capabilities(root.path)
    if os.unlink not in os.supports_dir_fd:
        message = "descriptor-bound physical-tree file deletion is unsupported"
        raise OSError(errno.ENOTSUP, message, root.path)
    if not hasattr(os, "fsync"):
        message = "physical-tree cleanup durability sync is unsupported"
        raise OSError(errno.ENOTSUP, message, root.path)
    bindings: dict[Path, tuple[int, int, int]] = {}
    for entry in (root, *manifest.entries):
        expected = (
            entry.parent_device,
            entry.parent_inode,
            entry.parent_mount_id,
        )
        prior = bindings.setdefault(entry.path.parent, expected)
        if prior != expected:
            _raise_changed(entry.path.parent)
    for path, expected in sorted(
        bindings.items(), key=lambda item: item[0].as_posix()
    ):
        with parent_descriptor.physical_directory(path) as opened:
            mount_id = tree_descriptor.mount_id(opened.descriptor, path)
            if (opened.state.st_dev, opened.state.st_ino, mount_id) != expected:
                _raise_changed(path)
            authenticated = file_descriptor.ParentDescriptor(
                path, opened.descriptor, opened.state, opened.ancestry
            )
            file_durability.sync_parent(authenticated)


def _delete_file(entry: m.Cli.AtomicPhysicalTreeEntry) -> None:
    with file_descriptor.parent_descriptor(entry.path, unlink=True) as parent:
        _require_parent(entry, parent.state.st_dev, parent.state.st_ino)
        parent_mount_id = tree_descriptor.mount_id(
            parent.descriptor, parent.path
        )
        if parent_mount_id != entry.parent_mount_id:
            _raise_changed(parent.path)
        observed = file_state.destination_state(entry.path, parent=parent)
        if observed is None:
            _raise_changed(entry.path)
        _require_file_state(entry, observed)
        size, digest = tree_descriptor.measure_authenticated_file(
            parent,
            entry.path,
            observed,
            required_mount_id=entry.mount_id,
        )
        if (size, digest) != (entry.size, entry.sha256):
            _raise_changed(entry.path)
        file_state.assert_destination_unchanged(
            entry.path, observed, parent=parent
        )
        file_descriptor.unlink_entry(parent, entry.path)
        file_durability.sync_parent(parent)
        if file_state.destination_state(entry.path, parent=parent) is not None:
            message = (
                "atomic physical-tree file still exists after delete: "
                f"{entry.path}"
            )
            raise OSError(errno.ESTALE, message, entry.path)


def _delete_directory(entry: m.Cli.AtomicPhysicalTreeEntry) -> None:
    current = directory_snapshot.read_authenticated_empty_directory(
        entry.path, required=True
    )
    if (
        not current.exists
        or current.mode is None
        or current.device is None
        or current.inode is None
    ):
        _raise_changed(entry.path)
    _require_parent(entry, current.parent_device, current.parent_inode)
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
        _raise_changed(entry.path)
    directory_delete.remove_guarded_empty_directory(current)


def _require_file_state(
    entry: m.Cli.AtomicPhysicalTreeEntry, observed: os.stat_result
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
        _raise_changed(entry.path)


def _require_parent(
    entry: m.Cli.AtomicPhysicalTreeEntry, device: int, inode: int
) -> None:
    if (entry.parent_device, entry.parent_inode) != (device, inode):
        _raise_changed(entry.path.parent)


def _deletion_key(entry: m.Cli.AtomicPhysicalTreeEntry) -> tuple[int, str]:
    return (len(entry.path.parts), entry.path.as_posix())


def _raise_changed(path: Path) -> Never:
    message = f"atomic physical-tree changed after manifest: {path}"
    raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["cleanup_physical_tree_guarded"]
