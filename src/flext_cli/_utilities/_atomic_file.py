"""Private atomic-file publication primitive for ``u.Cli`` file helpers."""

from __future__ import annotations

import errno
import os
import stat
import tempfile
from pathlib import Path

from flext_cli._utilities import _atomic_file_state as file_state


class _NoPrecondition:
    """Marker for callers that do not supply an expected version."""


_NO_PRECONDITION = _NoPrecondition()


def write_atomic_bytes(
    path: Path,
    content: bytes,
    *,
    expected_bytes: bytes | _NoPrecondition | None = _NO_PRECONDITION,
) -> None:
    """Replace bytes and retain mode for a uniquely owned regular destination.

    ``expected_bytes`` is an exact raw-byte precondition for a caller that holds
    the same exclusive cooperative lock from planning through publication.  The
    portable replace operation is not compare-and-swap against actors that ignore
    that lock.  The staged file is synced, but parent-directory durability across
    power loss is intentionally outside this primitive's contract.
    """
    path = path.absolute()
    guarded = not isinstance(expected_bytes, _NoPrecondition)
    if guarded:
        file_state.validate_parent(path.parent)
    expected = (
        file_state.destination_state(path)
        if guarded
        else file_state.permission_state(path)
    )
    expected_bytes_for_state: bytes | None = (
        expected_bytes if isinstance(expected_bytes, bytes) else None
    )
    file_state.validate_precondition(
        path, expected, expected_bytes_for_state, enabled=guarded
    )
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    temporary = Path(tmp_path)
    descriptor: int | None = fd
    temporary_identity: tuple[int, int] | None = None
    try:
        temporary_identity = file_state.identity(os.fstat(fd))
        _write_temporary(fd, temporary, content, expected)
        descriptor = None
        os.close(fd)
        _publish_temporary(
            path, temporary, expected, temporary_identity, guard_destination=guarded
        )
    except BaseException as operation_error:
        _remove_failed_temporary(
            temporary, temporary_identity, descriptor, operation_error
        )
        raise


def _write_temporary(
    fd: int, temporary: Path, content: bytes, expected: os.stat_result | None
) -> None:
    """Write every byte and apply the authorized destination permission mode."""
    remaining = memoryview(content)
    while remaining:
        written = os.write(fd, remaining)
        if written == 0:
            msg = f"atomic temporary write made no progress: {temporary}"
            raise OSError(errno.EIO, msg, temporary)
        remaining = remaining[written:]
    if expected is not None:
        _apply_permission_mode(fd, temporary, stat.S_IMODE(expected.st_mode))
    os.fsync(fd)


def _apply_permission_mode(descriptor: int, temporary: Path, mode: int) -> None:
    """Apply the host's permission-mode semantics through its supported API."""
    if os.chmod in os.supports_fd:
        os.chmod(descriptor, mode)
        return
    temporary.chmod(mode)


def _publish_temporary(
    path: Path,
    temporary: Path,
    expected: os.stat_result | None,
    identity: tuple[int, int],
    *,
    guard_destination: bool,
) -> None:
    """Authenticate both pathnames immediately before portable replacement."""
    file_state.assert_temporary_owned(temporary, identity)
    if guard_destination:
        file_state.assert_destination_unchanged(path, expected)
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
            file_state.assert_temporary_owned(temporary, identity)
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
