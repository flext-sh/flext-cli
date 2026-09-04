"""Private atomic-file publication primitive for ``u.Cli`` file helpers."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli import m
from . import _atomic_file_cleanup as file_cleanup
from . import _atomic_file_descriptor as file_descriptor
from . import _atomic_file_durability as file_durability
from . import _atomic_file_mode as file_mode
from . import _atomic_file_model as file_model
from . import _atomic_file_path as file_path
from . import _atomic_file_publish_checks as checks
from . import _atomic_file_state as file_state
from . import _atomic_file_temporary as file_temporary


class _NoPrecondition:
    """Marker for callers that do not supply an expected version."""


_NO_PRECONDITION = _NoPrecondition()


def write_atomic_bytes(
    path: Path,
    content: bytes,
    *,
    expected_state: m.Cli.AtomicFileState | _NoPrecondition = _NO_PRECONDITION,
    permission_mode: int | None = None,
) -> None:
    """Replace bytes and mode for a uniquely owned regular destination.

    ``expected_state`` is a complete physical precondition for a caller that
    holds the same exclusive cooperative lock from planning through publication.
    The descriptor-bound replace is not compare-and-swap against actors that
    ignore that lock. Both the staged inode and containing directory are synced.
    """
    path = file_path.validate_atomic_path(path)
    if not isinstance(content, bytes):
        message = "atomic file content must be bytes"
        raise OSError(errno.EINVAL, message, path)
    planned = _parse_precondition(path, expected_state)
    with file_descriptor.parent_descriptor(path, replace=True, unlink=True) as parent:
        expected = file_state.destination_state(path, parent=parent)
        if planned is None:
            guarded = False
            expected_content = None
            expected_mode: int | file_mode.NoModePrecondition | None = (
                file_mode.NO_MODE_PRECONDITION
            )
        else:
            guarded = True
            expected_content = planned.content
            expected_mode = planned.mode
            file_model.require_observed(planned, expected)
        file_state.validate_precondition(
            path, expected, expected_content, enabled=guarded, parent=parent
        )
        file_mode.validate_mode_precondition(path, expected, expected_mode)
        target_mode = file_mode.publication_mode(expected, permission_mode)
        file_temporary.require_mode_capability(path, target_mode)
        _stage_and_publish(parent, path, content, expected, target_mode)


def _parse_precondition(
    path: Path, expected_state: m.Cli.AtomicFileState | _NoPrecondition
) -> m.Cli.AtomicFileState | None:
    if expected_state is _NO_PRECONDITION:
        return None
    if isinstance(expected_state, _NoPrecondition):
        message = "expected_state sentinel must be the canonical singleton"
        raise OSError(errno.EINVAL, message, path)
    if not isinstance(expected_state, m.Cli.AtomicFileState):
        message = "expected_state must be an AtomicFileState"
        raise OSError(errno.EINVAL, message, path)
    if expected_state.path != path:
        message = "expected_state path differs from atomic destination"
        raise OSError(errno.EINVAL, message, path)
    file_mode.validate_guarded_mode_tuple(
        path, expected_state.content, expected_state.mode
    )
    return expected_state


def _stage_and_publish(
    parent: file_descriptor.ParentDescriptor,
    destination: Path,
    content: bytes,
    expected: os.stat_result | None,
    target_mode: int | None,
) -> None:
    temporary = file_temporary.temporary_path(parent)
    descriptor: int | None = None
    staged_identity: tuple[int, int] | None = None
    try:
        descriptor = file_temporary.create_descriptor(parent, temporary)
        staged_identity = file_state.identity(os.fstat(descriptor))
        staged_mode = _write_staged(
            parent, temporary, descriptor, staged_identity, content, target_mode
        )
        descriptor = None
    except BaseException as operation_error:
        file_cleanup.remove_failed_temporary(
            parent, temporary, staged_identity, descriptor, operation_error
        )
        raise
    replacement_completed = False
    try:
        _validate_replacement(
            parent,
            destination,
            expected,
            temporary,
            content,
            staged_mode,
            staged_identity,
        )
        file_descriptor.replace_entry(parent, temporary, parent, destination)
        replacement_completed = True
        file_durability.sync_replacement(parent, parent)
        checks.validate_publication(
            parent,
            destination,
            parent,
            temporary,
            content,
            staged_mode,
            staged_identity,
        )
    except BaseException as operation_error:
        if not replacement_completed:
            file_cleanup.remove_failed_temporary(
                parent, temporary, staged_identity, descriptor, operation_error
            )
        raise


def _write_staged(
    parent: file_descriptor.ParentDescriptor,
    temporary: Path,
    descriptor: int,
    identity: tuple[int, int],
    content: bytes,
    target_mode: int | None,
) -> int:
    file_state.assert_temporary_owned(temporary, identity, parent=parent)
    staged_mode = file_temporary.write_and_sync(
        descriptor, temporary, content, target_mode
    )
    os.close(descriptor)
    return staged_mode


def _validate_replacement(
    parent: file_descriptor.ParentDescriptor,
    destination: Path,
    expected: os.stat_result | None,
    temporary: Path,
    content: bytes,
    staged_mode: int,
    staged_identity: tuple[int, int],
) -> None:
    staged_state = _validate_staged(
        parent, temporary, content, staged_mode, staged_identity
    )
    checks.require_distinct_inode(destination, expected, staged_identity)
    checks.validate_devices(
        destination, parent, expected, temporary, parent, staged_state
    )
    file_state.assert_destination_unchanged(destination, expected, parent=parent)
    file_state.assert_temporary_owned(temporary, staged_identity, parent=parent)


def _validate_staged(
    parent: file_descriptor.ParentDescriptor,
    temporary: Path,
    content: bytes,
    mode: int,
    identity: tuple[int, int],
) -> os.stat_result:
    state = file_state.destination_state(temporary, parent=parent)
    if state is None:
        message = f"atomic temporary disappeared before publication: {temporary}"
        raise FileNotFoundError(errno.ENOENT, message, temporary)
    checks.require_identity(temporary, state, identity)
    file_state.validate_precondition(
        temporary, state, content, enabled=True, parent=parent
    )
    file_mode.validate_mode_precondition(temporary, state, mode)
    return state


__all__: list[str] = ["write_atomic_bytes"]
