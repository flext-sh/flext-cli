"""Public descriptor-owned staging for one atomic file replacement."""

from __future__ import annotations

import errno
import os
import secrets
import signal
import stat
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from flext_cli import t

from . import (
    atomic_file_descriptor as file_descriptor,
    atomic_file_mode as file_mode,
    atomic_file_state as file_state,
)

_SECURE_CREATE_MODE = 0o600


def temporary_path(parent: file_descriptor.ParentDescriptor) -> Path:
    """Return one unpredictable sibling name without probing or retrying."""
    return parent.path / f".flext-atomic-{secrets.token_hex(16)}.tmp"


def require_mode_capability(path: Path, permission_mode: int | None) -> None:
    """Fail before staging if an exact requested mode cannot use its descriptor."""
    if permission_mode is not None and os.chmod not in os.supports_fd:
        message = "descriptor permission changes are unsupported"
        raise OSError(errno.ENOTSUP, message, path)


def create_descriptor(parent: file_descriptor.ParentDescriptor, temporary: Path) -> int:
    """Create one exclusive, securely permissioned sibling through ``dir_fd``."""
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )
    return file_descriptor.open_entry(
        parent, temporary, flags, mode=_SECURE_CREATE_MODE
    )


@contextmanager
def authenticated_descriptor(
    parent: file_descriptor.ParentDescriptor, temporary: Path
) -> Generator[t.Pair[int, t.Pair[int, int]]]:
    """Transfer one descriptor only after its identity is bound.

    POSIX timer signals are held across ``open`` and the caller's assignment of
    both fields.  Restoring the mask can therefore propagate the original
    timeout only after cleanup has an authenticated inode and live descriptor.
    Windows has no ``pthread_sigmask`` or POSIX interval-timer delivery.
    """
    timer_signals = {
        candidate
        for name in ("SIGALRM", "SIGVTALRM", "SIGPROF")
        if (candidate := getattr(signal, name, None)) is not None
    }
    previous_mask = (
        signal.pthread_sigmask(signal.SIG_BLOCK, timer_signals)
        if timer_signals and hasattr(signal, "pthread_sigmask")
        else None
    )
    descriptor: int | None = None
    transferred = False
    try:
        descriptor = create_descriptor(parent, temporary)
        authenticated = (descriptor, file_state.identity(os.fstat(descriptor)))
        yield authenticated
        transferred = True
    finally:
        if descriptor is not None and not transferred:
            os.close(descriptor)
        if previous_mask is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)


def write_and_sync(
    descriptor: int, temporary: Path, content: bytes, permission_mode: int | None
) -> int:
    """Write exact bytes, materialize exact mode, and sync the open inode."""
    remaining = memoryview(content)
    while remaining:
        written = os.write(descriptor, remaining)
        if written == 0:
            message = f"atomic temporary write made no progress: {temporary}"
            raise OSError(errno.EIO, message, temporary)
        remaining = remaining[written:]
    if permission_mode is not None:
        os.chmod(descriptor, permission_mode)
        file_mode.assert_observed_mode(temporary, os.fstat(descriptor), permission_mode)
    os.fsync(descriptor)
    return stat.S_IMODE(os.fstat(descriptor).st_mode)


__all__: list[str] = [
    "authenticated_descriptor",
    "create_descriptor",
    "require_mode_capability",
    "temporary_path",
    "write_and_sync",
]
