"""Guarded no-clobber publication of caller-owned staged directories."""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import Never

from flext_cli import m
from . import atomic_directory_descriptor as directory_descriptor
from . import atomic_directory_model as directory_model
from . import atomic_directory_state as directory_state
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_durability as file_durability
from . import atomic_file_path as file_path


def publish_guarded_staged_empty_directory(
    destination_before: m.Cli.AtomicDirectoryState,
    staged: m.Cli.AtomicDirectoryState,
) -> m.Cli.AtomicDirectoryState:
    """Move one exact empty directory into an exact absent destination.

    Linux uses ``renameat2(RENAME_NOREPLACE)`` so a concurrent destination can
    never be overwritten. Windows is accepted only when descriptor-relative
    ``os.rename`` is available with its documented no-replace behavior. Other
    platforms fail before effects. Source identity still requires every writer
    to honor the caller's exclusive cooperative lock.
    """
    destination = file_path.validate_atomic_path(destination_before.path)
    staged_path = file_path.validate_atomic_path(staged.path)
    if destination == staged_path:
        message = "staged directory and destination must differ"
        raise OSError(errno.EINVAL, message, destination)
    directory_model.require_absent(destination_before, purpose="published")
    directory_model.require_existing(staged, purpose="staged")
    directory_descriptor.require_publish_capabilities(staged_path, destination)
    with (
        file_descriptor.parent_descriptor(destination) as destination_parent,
        file_descriptor.parent_descriptor(staged_path) as staged_parent,
    ):
        directory_model.require_parent(destination_before, destination_parent.state)
        directory_model.require_parent(staged, staged_parent.state)
        _require_destination_absent(
            destination_before, destination_parent, destination
        )
        authenticated = _authenticated_staged(staged, staged_parent, staged_path)
        _require_same_filesystem(
            destination, destination_parent, staged_parent, authenticated
        )
        file_durability.sync_replacement(staged_parent, destination_parent)
        _require_destination_absent(
            destination_before, destination_parent, destination
        )
        authenticated = _authenticated_staged(staged, staged_parent, staged_path)
        directory_descriptor.rename_entry_noreplace(
            staged_parent, staged_path, destination_parent, destination
        )
        try:
            file_durability.sync_replacement(staged_parent, destination_parent)
            return _published_state(
                destination_parent,
                destination,
                staged_parent,
                staged_path,
                staged,
            )
        except OSError as post_error:
            _raise_post_publication_failure(destination, post_error)


def _require_destination_absent(
    planned: m.Cli.AtomicDirectoryState,
    parent: file_descriptor.ParentDescriptor,
    path: Path,
) -> None:
    observed = directory_state.destination_state(path, parent=parent)
    directory_model.require_observed(planned, observed)
    file_descriptor.assert_parent_unchanged(parent)


def _authenticated_staged(
    planned: m.Cli.AtomicDirectoryState,
    parent: file_descriptor.ParentDescriptor,
    path: Path,
) -> os.stat_result:
    observed = directory_state.destination_state(path, parent=parent)
    directory_model.require_observed(planned, observed)
    if observed is None:
        message = f"atomic staged directory disappeared: {path}"
        raise OSError(errno.ESTALE, message, path)
    authenticated = directory_state.read_empty_state(parent, path, observed)
    directory_model.require_observed(planned, authenticated)
    return authenticated


def _require_same_filesystem(
    destination: Path,
    destination_parent: file_descriptor.ParentDescriptor,
    staged_parent: file_descriptor.ParentDescriptor,
    staged: os.stat_result,
) -> None:
    device = destination_parent.state.st_dev
    if staged_parent.state.st_dev != device or staged.st_dev != device:
        message = "staged directory and destination span filesystems"
        raise OSError(errno.EXDEV, message, destination)


def _published_state(
    destination_parent: file_descriptor.ParentDescriptor,
    destination: Path,
    staged_parent: file_descriptor.ParentDescriptor,
    staged_path: Path,
    staged: m.Cli.AtomicDirectoryState,
) -> m.Cli.AtomicDirectoryState:
    if directory_state.destination_state(staged_path, parent=staged_parent) is not None:
        message = f"staged directory name exists after publication: {staged_path}"
        raise OSError(errno.ESTALE, message, staged_path)
    observed = directory_state.destination_state(destination, parent=destination_parent)
    if observed is None:
        message = f"published directory is missing: {destination}"
        raise OSError(errno.ESTALE, message, destination)
    authenticated = directory_state.read_empty_state(
        destination_parent, destination, observed
    )
    directory_model.require_observed(staged, authenticated)
    return directory_model.from_observed(
        destination, destination_parent.state, authenticated
    )


def _raise_post_publication_failure(destination: Path, error: OSError) -> Never:
    message = (
        "atomic directory rename completed but durability or live-state proof failed: "
        f"{error}"
    )
    raise OSError(errno.EIO, message, destination) from error


__all__: list[str] = ["publish_guarded_staged_empty_directory"]
