"""Private atomic-file publication primitive for ``u.Cli`` file helpers."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli._utilities._atomic_file_state import (
    assert_destination_unchanged,
    assert_temporary_owned,
    destination_state,
    identity,
    permission_state,
    validate_parent,
    validate_precondition,
)


class _NoPrecondition:
    """Marker for callers that do not supply an expected version."""


_NO_PRECONDITION = _NoPrecondition()


def write_atomic_bytes(
    path: Path,
    content: bytes,
    *,
    expected_bytes: bytes | _NoPrecondition | None = _NO_PRECONDITION,
    expected_mode: int | file_mode.NoModePrecondition | None = (
        file_mode.NO_MODE_PRECONDITION
    ),
    permission_mode: int | None = None,
) -> None:
    """Replace bytes and mode for a uniquely owned regular destination.

    ``expected_bytes`` is an exact raw-byte precondition for a caller that holds
    the same exclusive cooperative lock from planning through publication. The
    descriptor-bound replace is not compare-and-swap against actors that ignore
    that lock. The staged file is synced; parent-directory durability across
    power loss is outside this primitive's contract.
    """
    path = file_path.validate_atomic_path(path)
    guarded, expected_content = _parse_precondition(path, expected_bytes)
    if not guarded and expected_mode is not file_mode.NO_MODE_PRECONDITION:
        message = "expected_mode requires an expected_bytes precondition"
        raise OSError(errno.EINVAL, message, path)
    if guarded:
        file_mode.validate_guarded_mode_tuple(
            path, expected_content, expected_mode
        )
    with file_descriptor.parent_descriptor(
        path, replace=True, unlink=True
    ) as parent:
        expected = file_state.destination_state(path, parent=parent)
        file_state.validate_precondition(
            path,
            expected,
            expected_content,
            enabled=guarded,
            parent=parent,
        )
        file_mode.validate_mode_precondition(path, expected, expected_mode)
        target_mode = file_mode.publication_mode(expected, permission_mode)
        file_temporary.require_mode_capability(path, target_mode)
        _stage_and_publish(parent, path, content, expected, target_mode)


def _parse_precondition(
    path: Path, expected_bytes: bytes | _NoPrecondition | None
) -> tuple[bool, bytes | None]:
    if expected_bytes is _NO_PRECONDITION:
        return False, None
    if isinstance(expected_bytes, _NoPrecondition):
        message = "expected_bytes sentinel must be the canonical singleton"
        raise OSError(errno.EINVAL, message, path)
    if expected_bytes is None or isinstance(expected_bytes, bytes):
        return True, expected_bytes
    message = "expected_bytes must be bytes or None"
    raise OSError(errno.EINVAL, message, path)


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
    replacement_completed = False
    try:
        descriptor = file_temporary.create_descriptor(parent, temporary)
        staged_identity = file_state.identity(os.fstat(descriptor))
        file_state.assert_temporary_owned(
            temporary, staged_identity, parent=parent
        )
        staged_mode = file_temporary.write_and_sync(
            descriptor, temporary, content, target_mode
        )
        os.close(descriptor)
        descriptor = None
        staged_state = _validate_staged(
            parent, temporary, content, staged_mode, staged_identity
        )
        checks.require_distinct_inode(destination, expected, staged_identity)
        checks.validate_devices(
            destination,
            parent,
            expected,
            temporary,
            parent,
            staged_state,
        )
        file_state.assert_destination_unchanged(
            destination, expected, parent=parent
        )
        file_state.assert_temporary_owned(
            temporary, staged_identity, parent=parent
        )
        file_descriptor.replace_entry(parent, temporary, parent, destination)
        replacement_completed = True
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
                parent,
                temporary,
                staged_identity,
                descriptor,
                operation_error,
            )
        raise


def _validate_staged(
    parent: file_descriptor.ParentDescriptor,
    temporary: Path,
    content: bytes,
    mode: int,
    identity: tuple[int, int],
    *,
    guard_destination: bool,
) -> None:
    """Authenticate both pathnames immediately before portable replacement."""
    assert_temporary_owned(temporary, identity)
    if guard_destination:
        assert_destination_unchanged(path, expected)
    temporary.replace(path)


def _remove_failed_temporary(
    temporary: Path,
    identity: tuple[int, int] | None,
    descriptor: int | None,
    operation_error: BaseException,
) -> None:
    """Close and remove owned staging state while retaining every failure cause."""
    cleanup_errors: list[OSError] = []
    if descriptor is not None:
        try:
            os.close(descriptor)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if identity is None:
        msg = f"refusing to remove unauthenticated atomic temporary: {temporary}"
        cleanup_errors.append(OSError(errno.ESTALE, msg, temporary))
    else:
        try:
            assert_temporary_owned(temporary, identity)
            temporary.unlink()
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if cleanup_errors:
        cleanup_summary = "; ".join(str(error) for error in cleanup_errors)
        message = (
            f"atomic write failed ({operation_error}); "
            f"temporary cleanup failed ({cleanup_summary})"
        )
        if isinstance(operation_error, Exception):
            causes = ExceptionGroup(
                "atomic write and temporary cleanup failed",
                [operation_error, *cleanup_errors],
            )
            raise OSError(errno.EIO, message, temporary) from causes
        group_message = "atomic write and temporary cleanup failed"
        raise BaseExceptionGroup(
            group_message, [operation_error, *cleanup_errors]
        ) from cleanup_errors[-1]


__all__: list[str] = ["write_atomic_bytes"]
