"""Atomic-file publication primitive for ``u.Cli`` file helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import signal
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import FlextCliUtilitiesAtomicFileDescriptor

if TYPE_CHECKING:
    from flext_cli import m, t


class FlextCliUtilitiesAtomicFile:
    """Canonical namespace owner."""

    class _NoPrecondition:
        """Marker for callers that do not supply an expected version."""

    _NO_PRECONDITION = _NoPrecondition()

    @staticmethod
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
        from flext_cli._utilities import FlextCliUtilitiesAtomicFileMode, FlextCliUtilitiesAtomicFileModel, FlextCliUtilitiesAtomicFilePath, FlextCliUtilitiesAtomicFileState, FlextCliUtilitiesAtomicFileTemporary
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(path)
        if not isinstance(content, bytes):
            message = "atomic file content must be bytes"
            raise OSError(errno.EINVAL, message, path)
        planned = FlextCliUtilitiesAtomicFile._parse_precondition(path, expected_state)
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            path,
            replace=True,
            unlink=True,
        ) as parent:
            expected = FlextCliUtilitiesAtomicFileState.destination_state(
                path,
                parent=parent,
            )
            if planned is None:
                guarded = False
                expected_content = None
                expected_mode: (
                    int | FlextCliUtilitiesAtomicFileMode.NoModePrecondition | None
                ) = FlextCliUtilitiesAtomicFileMode.NO_MODE_PRECONDITION
            else:
                guarded = True
                expected_content = planned.content
                expected_mode = planned.mode
                FlextCliUtilitiesAtomicFileModel.require_parent(planned, parent.state)
                FlextCliUtilitiesAtomicFileModel.require_observed(planned, expected)
            FlextCliUtilitiesAtomicFileState.validate_precondition(
                path,
                expected,
                expected_content,
                enabled=guarded,
                parent=parent,
            )
            FlextCliUtilitiesAtomicFileMode.validate_mode_precondition(
                path,
                expected,
                expected_mode,
            )
            target_mode = FlextCliUtilitiesAtomicFileMode.publication_mode(
                expected,
                permission_mode,
            )
            FlextCliUtilitiesAtomicFileTemporary.require_mode_capability(
                path,
                target_mode,
            )
            FlextCliUtilitiesAtomicFile._stage_and_publish(
                parent,
                path,
                content,
                expected,
                target_mode,
            )

    @staticmethod
    def _parse_precondition(
        path: Path,
        expected_state: m.Cli.AtomicFileState | _NoPrecondition,
    ) -> m.Cli.AtomicFileState | None:
        from flext_cli._utilities import FlextCliUtilitiesAtomicFileMode
        if expected_state is FlextCliUtilitiesAtomicFile._NO_PRECONDITION:
            return None
        if isinstance(expected_state, FlextCliUtilitiesAtomicFile._NoPrecondition):
            message = "expected_state sentinel must be the canonical singleton"
            raise OSError(errno.EINVAL, message, path)
        if expected_state.path != path:
            message = "expected_state path differs from atomic destination"
            raise OSError(errno.EINVAL, message, path)
        FlextCliUtilitiesAtomicFileMode.validate_guarded_mode_tuple(
            path,
            expected_state.content,
            expected_state.mode,
        )
        return expected_state

    @staticmethod
    def _stage_and_publish(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        destination: Path,
        content: bytes,
        expected: os.stat_result | None,
        target_mode: int | None,
    ) -> None:
        """Retain the staging owner through acquisition, publication and cleanup."""
        stage = FlextCliUtilitiesAtomicFile._AtomicStage(parent)
        try:
            stage.acquire()
            stage.write(content, target_mode)
            stage.publish(destination, expected, content)
        except BaseException as operation_error:
            stage.cleanup(operation_error)
            raise

    class _AtomicStage:
        """Own live staging state before any signal can cross a method boundary."""

        def __init__(
            self,
            parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        ) -> None:
            from flext_cli._utilities import FlextCliUtilitiesAtomicFileTemporary
            self.parent = parent
            self.temporary = FlextCliUtilitiesAtomicFileTemporary.temporary_path(parent)
            self.descriptor: int | None = None
            self.identity: t.Pair[int, int] | None = None
            self.mode: int | None = None
            self.replacement_completed = False

        def acquire(self) -> None:
            """Authenticate the descriptor before restoring pending timer delivery."""
            from flext_cli._utilities import FlextCliUtilitiesAtomicFileState, FlextCliUtilitiesAtomicFileTemporary
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
                self.descriptor = (
                    FlextCliUtilitiesAtomicFileTemporary.create_descriptor(
                        self.parent,
                        self.temporary,
                    )
                )
                self.identity = FlextCliUtilitiesAtomicFileState.identity(
                    os.fstat(self.descriptor),
                )
            finally:
                if previous_mask is not None:
                    signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

        def write(self, content: bytes, target_mode: int | None) -> None:
            """Write only the authenticated inode and release its descriptor.

            Raises:
                RuntimeError: If atomic staging must be acquired before writing.

            """
            from flext_cli._utilities import FlextCliUtilitiesAtomicFileState, FlextCliUtilitiesAtomicFileTemporary
            if self.descriptor is None or self.identity is None:
                message = "atomic staging must be acquired before writing"
                raise RuntimeError(message)
            FlextCliUtilitiesAtomicFileState.assert_temporary_owned(
                self.temporary,
                self.identity,
                parent=self.parent,
            )
            self.mode = FlextCliUtilitiesAtomicFileTemporary.write_and_sync(
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
            from flext_cli._utilities import FlextCliUtilitiesAtomicFileDurability, FlextCliUtilitiesAtomicFilePublishChecks
            if self.identity is None or self.mode is None:
                message = "atomic staging must be written before publication"
                raise RuntimeError(message)
            FlextCliUtilitiesAtomicFile._validate_replacement(
                self.parent,
                destination,
                expected,
                self.temporary,
                content,
                self.mode,
                self.identity,
            )
            FlextCliUtilitiesAtomicFileDescriptor.replace_entry(
                self.parent,
                self.temporary,
                self.parent,
                destination,
            )
            self.replacement_completed = True
            FlextCliUtilitiesAtomicFileDurability.sync_replacement(
                self.parent,
                self.parent,
            )
            FlextCliUtilitiesAtomicFilePublishChecks.validate_publication(
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
            from flext_cli._utilities import FlextCliUtilitiesAtomicFileCleanup
            if not self.replacement_completed:
                FlextCliUtilitiesAtomicFileCleanup.remove_failed_temporary(
                    self.parent,
                    self.temporary,
                    self.identity,
                    self.descriptor,
                    operation_error,
                )

    @staticmethod
    def _validate_replacement(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        destination: Path,
        expected: os.stat_result | None,
        temporary: Path,
        content: bytes,
        staged_mode: int,
        staged_identity: t.Pair[int, int],
    ) -> None:
        from flext_cli._utilities import FlextCliUtilitiesAtomicFilePublishChecks, FlextCliUtilitiesAtomicFileState
        staged_state = FlextCliUtilitiesAtomicFile._validate_staged(
            parent,
            temporary,
            content,
            staged_mode,
            staged_identity,
        )
        FlextCliUtilitiesAtomicFilePublishChecks.require_distinct_inode(
            destination,
            expected,
            staged_identity,
        )
        FlextCliUtilitiesAtomicFilePublishChecks.validate_devices(
            destination,
            parent,
            expected,
            temporary,
            parent,
            staged_state,
        )
        FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
            destination,
            expected,
            parent=parent,
        )
        FlextCliUtilitiesAtomicFileState.assert_temporary_owned(
            temporary,
            staged_identity,
            parent=parent,
        )

    @staticmethod
    def _validate_staged(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        temporary: Path,
        content: bytes,
        mode: int,
        identity: t.Pair[int, int],
    ) -> os.stat_result:
        from flext_cli._utilities import FlextCliUtilitiesAtomicFileMode, FlextCliUtilitiesAtomicFilePublishChecks, FlextCliUtilitiesAtomicFileState
        state = FlextCliUtilitiesAtomicFileState.destination_state(
            temporary,
            parent=parent,
        )
        if state is None:
            message = f"atomic temporary disappeared before publication: {temporary}"
            raise FileNotFoundError(errno.ENOENT, message, temporary)
        FlextCliUtilitiesAtomicFilePublishChecks.require_identity(
            temporary,
            state,
            identity,
        )
        FlextCliUtilitiesAtomicFileState.validate_precondition(
            temporary,
            state,
            content,
            enabled=True,
            parent=parent,
        )
        FlextCliUtilitiesAtomicFileMode.validate_mode_precondition(
            temporary,
            state,
            mode,
        )
        return state


__all__: list[str] = ["FlextCliUtilitiesAtomicFile"]
