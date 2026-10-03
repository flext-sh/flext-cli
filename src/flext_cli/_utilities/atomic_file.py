"""Atomic-file publication primitive for ``u.Cli`` file helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import signal
from pathlib import Path

from flext_cli._utilities import (
    atomic_file_cleanup as file_cleanup,
    atomic_file_descriptor as file_descriptor,
    atomic_file_durability as file_durability,
    atomic_file_mode as file_mode,
    atomic_file_model as file_model,
    atomic_file_path as file_path,
    atomic_file_publish_checks as checks,
    atomic_file_state as file_state,
    atomic_file_temporary as file_temporary,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import m, t


class _NoPrecondition:
    """Marker for callers that do not supply an expected version."""


_NO_PRECONDITION = _NoPrecondition()


def write_atomic_bytes(
    path: Path,
    content: object,
    *,
    expected_state: m.Cli.AtomicFileState | _NoPrecondition = _NO_PRECONDITION,
    permission_mode: int | None = None,
) -> None:
    """Replace bytes and mode for a uniquely owned regular destination.

    ``expected_state`` is a complete physical precondition for a caller that
    holds the same exclusive cooperative lock from planning through publication.
    The descriptor-bound replace is not compare-and-swap against actors that
    ignore that lock. Both the staged inode and containing directory are synced.

    Raises:
        OSError: If ``not isinstance(content, bytes)``.

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
            expected_mode: int | file_mode.FlextCliNoModePrecondition | None = (
                file_mode.NO_MODE_PRECONDITION
            )
        else:
            guarded = True
            expected_content = planned.content
            expected_mode = planned.mode
            file_model.require_parent(planned, parent.state)
            file_model.require_observed(planned, expected)
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
    path: Path,
    expected_state: m.Cli.AtomicFileState | _NoPrecondition,
) -> m.Cli.AtomicFileState | None:
    if expected_state is _NO_PRECONDITION:
        return None
    if isinstance(expected_state, _NoPrecondition):
        message = "expected_state sentinel must be the canonical singleton"
        raise OSError(errno.EINVAL, message, path)
    if expected_state.path != path:
        message = "expected_state path differs from atomic destination"
        raise OSError(errno.EINVAL, message, path)
    file_mode.validate_guarded_mode_tuple(
        path,
        expected_state.content,
        expected_state.mode,
    )
    return expected_state


def _stage_and_publish(
    parent: file_descriptor.FlextCliParentDescriptor,
    destination: Path,
    content: bytes,
    expected: os.stat_result | None,
    target_mode: int | None,
) -> None:
    """Retain the staging owner through acquisition, publication and cleanup."""
    stage = _AtomicStage(parent)
    try:
        stage.acquire()
        stage.write(content, target_mode)
        stage.publish(destination, expected, content)
    except BaseException as operation_error:
        stage.cleanup(operation_error)
        raise


class _AtomicStage:
    """Own live staging state before any signal can cross a method boundary."""

    def __init__(self, parent: file_descriptor.FlextCliParentDescriptor) -> None:
        self.parent = parent
        self.temporary = file_temporary.temporary_path(parent)
        self.descriptor: int | None = None
        self.identity: t.Pair[int, int] | None = None
        self.mode: int | None = None
        self.replacement_completed = False

    def acquire(self) -> None:
        """Authenticate the descriptor before restoring pending timer delivery."""
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
        try:
            self.descriptor = file_temporary.create_descriptor(
                self.parent,
                self.temporary,
            )
            self.identity = file_state.identity(os.fstat(self.descriptor))
        finally:
            if previous_mask is not None:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

    def write(self, content: bytes, target_mode: int | None) -> None:
        """Write only the authenticated inode and release its descriptor.

        Raises:
            RuntimeError: If atomic staging must be acquired before writing.

        """
        if self.descriptor is None or self.identity is None:
            message = "atomic staging must be acquired before writing"
            raise RuntimeError(message)
        file_state.assert_temporary_owned(
            self.temporary,
            self.identity,
            parent=self.parent,
        )
        self.mode = file_temporary.write_and_sync(
            self.descriptor,
            self.temporary,
            content,
            target_mode,
        )
        os.close(self.descriptor)
        self.descriptor = None

    def publish(
        self,
        destination: Path,
        expected: os.stat_result | None,
        content: bytes,
    ) -> None:
        """Publish the authenticated bytes and retain completion before proof.

        Raises:
            RuntimeError: If atomic staging must be written before publication.

        """
        if self.identity is None or self.mode is None:
            message = "atomic staging must be written before publication"
            raise RuntimeError(message)
        _validate_replacement(
            self.parent,
            destination,
            expected,
            self.temporary,
            content,
            self.mode,
            self.identity,
        )
        file_descriptor.replace_entry(
            self.parent,
            self.temporary,
            self.parent,
            destination,
        )
        self.replacement_completed = True
        file_durability.sync_replacement(self.parent, self.parent)
        checks.validate_publication(
            self.parent,
            destination,
            self.parent,
            self.temporary,
            content,
            self.mode,
            self.identity,
        )

    def cleanup(self, operation_error: BaseException) -> None:
        """Remove only authenticated staging while preserving the first cause."""
        if not self.replacement_completed:
            file_cleanup.remove_failed_temporary(
                self.parent,
                self.temporary,
                self.identity,
                self.descriptor,
                operation_error,
            )


def _validate_replacement(
    parent: file_descriptor.FlextCliParentDescriptor,
    destination: Path,
    expected: os.stat_result | None,
    temporary: Path,
    content: bytes,
    staged_mode: int,
    staged_identity: t.Pair[int, int],
) -> None:
    staged_state = _validate_staged(
        parent,
        temporary,
        content,
        staged_mode,
        staged_identity,
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
    file_state.assert_destination_unchanged(destination, expected, parent=parent)
    file_state.assert_temporary_owned(temporary, staged_identity, parent=parent)


def _validate_staged(
    parent: file_descriptor.FlextCliParentDescriptor,
    temporary: Path,
    content: bytes,
    mode: int,
    identity: t.Pair[int, int],
) -> os.stat_result:
    state = file_state.destination_state(temporary, parent=parent)
    if state is None:
        message = f"atomic temporary disappeared before publication: {temporary}"
        raise FileNotFoundError(errno.ENOENT, message, temporary)
    checks.require_identity(temporary, state, identity)
    file_state.validate_precondition(
        temporary,
        state,
        content,
        enabled=True,
        parent=parent,
    )
    file_mode.validate_mode_precondition(temporary, state, mode)
    return state


__all__: list[str] = ["write_atomic_bytes"]
