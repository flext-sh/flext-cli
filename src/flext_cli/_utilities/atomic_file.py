"""Atomic-file publication primitive for ``u.Cli`` file helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import signal
import stat
from collections.abc import MutableSequence
from pathlib import Path

from flext_cli import c, m
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFileCleanup,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFileMode,
    FlextCliUtilitiesAtomicFileModel,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFilePublishChecks,
    FlextCliUtilitiesAtomicFileState,
    FlextCliUtilitiesAtomicFileTemporary,
)


class FlextCliUtilitiesAtomicFile:
    """Canonical namespace owner."""

    @staticmethod
    def write_atomic_state(
        path: Path,
        content: bytes,
        options: m.Cli.AtomicWriteOptions | None = None,
        *,
        published_paths: MutableSequence[Path] | None = None,
    ) -> m.Cli.AtomicFileState:
        """Replace bytes and mode for a uniquely owned regular destination.

        ``options`` carries the precondition, mode, durability and owner policy
        declared by ``m.Cli.AtomicWriteOptions``. The descriptor-bound replace is
        not compare-and-swap against actors that ignore the cooperative lock.
        ``published_paths`` receives the native physical effect before a later
        durability or validation failure; it never attests successful completion.

        Returns:
            The original bytes and descriptor-authenticated published state.

        """
        opts = options or m.Cli.AtomicWriteOptions()
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(path)
        planned = FlextCliUtilitiesAtomicFile._parse_precondition(
            path, opts.expected_state
        )
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            path,
            replace=True,
            unlink=True,
        ) as parent:
            expected = FlextCliUtilitiesAtomicFileState.file_destination_state(
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
                opts.permission_mode,
            )
            FlextCliUtilitiesAtomicFileTemporary.require_mode_capability(
                path,
                target_mode,
            )
            published = FlextCliUtilitiesAtomicFile._stage_and_publish(
                FlextCliUtilitiesAtomicFile._AtomicStage(
                    parent,
                    durable=opts.durability is c.Cli.WriteDurability.DURABLE,
                    published_paths=published_paths,
                ),
                path,
                content,
                expected,
                target_mode,
            )
            if opts.owner_uid is not None:
                FlextCliUtilitiesAtomicFileState.require_owner(
                    path.parent, os.fstat(parent.descriptor), opts.owner_uid
                )
                FlextCliUtilitiesAtomicFileState.require_owner(
                    path, published, opts.owner_uid
                )
            return m.Cli.AtomicFileState(
                path=path,
                content=content,
                parent_device=parent.state.st_dev,
                parent_inode=parent.state.st_ino,
                mode=stat.S_IMODE(published.st_mode),
                device=published.st_dev,
                inode=published.st_ino,
                link_count=published.st_nlink,
                file_attributes=getattr(published, "st_file_attributes", None),
                reparse_tag=getattr(published, "st_reparse_tag", None),
            )

    @staticmethod
    def _parse_precondition(
        path: Path,
        expected_state: m.Cli.AtomicFileState | None,
    ) -> m.Cli.AtomicFileState | None:
        if expected_state is None:
            return None
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
        stage: FlextCliUtilitiesAtomicFile._AtomicStage,
        destination: Path,
        content: bytes,
        expected: os.stat_result | None,
        target_mode: int | None,
    ) -> os.stat_result:
        """Retain staging ownership through publication and its original proof.

        Returns:
            The stat authenticated by native publication validation.

        """
        if expected is None:
            FlextCliUtilitiesAtomicFileDescriptor.require_file_create_capabilities(
                destination
            )
        try:
            stage.acquire()
            stage.write(content, target_mode)
            return stage.publish(destination, expected, content)
        except BaseException as operation_error:
            stage.cleanup(operation_error)
            raise

    class _AtomicStage:
        """Own live staging state before any signal can cross a method boundary."""

        def __init__(
            self,
            parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
            *,
            durable: bool,
            published_paths: MutableSequence[Path] | None = None,
        ) -> None:
            self.parent = parent
            self.durable = durable
            self.temporary = FlextCliUtilitiesAtomicFileTemporary.temporary_path(parent)
            self.descriptor: int | None = None
            self.identity: tuple[int, int] | None = None
            self.mode: int | None = None
            self.replacement_completed = False
            self.published_paths = published_paths
            self.linked_temporary = False

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
                self.descriptor = (
                    FlextCliUtilitiesAtomicFileTemporary.create_descriptor(
                        self.parent,
                        self.temporary,
                    )
                )
                self.identity = FlextCliUtilitiesAtomicFileState.file_state_identity(
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
                durable=self.durable,
            )
            os.close(self.descriptor)
            self.descriptor = None

        def publish(
            self,
            destination: Path,
            expected: os.stat_result | None,
            content: bytes,
        ) -> os.stat_result:
            """Publish the authenticated bytes and retain completion before proof.

            Returns:
                The stat authenticated against the original staging inode.

            Raises:
                RuntimeError: If atomic staging must be written before publication.

            """
            if self.identity is None or self.mode is None:
                message = "atomic staging must be written before publication"
                raise RuntimeError(message)
            staged = m.Cli.StagedFile(
                path=self.temporary,
                content=content,
                mode=self.mode,
                identity=self.identity,
            )
            FlextCliUtilitiesAtomicFile._validate_replacement(
                self.parent,
                destination,
                expected,
                staged,
            )
            if expected is None:
                publication_signals = {
                    candidate
                    for name in (
                        "SIGINT",
                        "SIGTERM",
                        "SIGHUP",
                        "SIGALRM",
                        "SIGVTALRM",
                        "SIGPROF",
                    )
                    if (candidate := getattr(signal, name, None)) is not None
                }
                previous_mask = (
                    signal.pthread_sigmask(signal.SIG_BLOCK, publication_signals)
                    if publication_signals and hasattr(signal, "pthread_sigmask")
                    else None
                )
                try:
                    FlextCliUtilitiesAtomicFileDescriptor.link_entry(
                        self.parent,
                        self.temporary,
                        self.parent,
                        destination,
                    )
                    self.record_publication(destination)
                    self.linked_temporary = True
                    FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(
                        self.parent,
                        self.temporary,
                    )
                    self.linked_temporary = False
                finally:
                    if previous_mask is not None:
                        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
            else:
                FlextCliUtilitiesAtomicFileDescriptor.replace_entry(
                    self.parent,
                    self.temporary,
                    self.parent,
                    destination,
                )
                self.record_publication(destination)
            if self.durable:
                FlextCliUtilitiesAtomicFileDurability.sync_replacement(
                    self.parent,
                    self.parent,
                )
            return FlextCliUtilitiesAtomicFilePublishChecks.validate_publication(
                self.parent,
                destination,
                self.parent,
                staged,
            )

        def record_publication(self, destination: Path) -> None:
            """Retain the native completion witness before any later failure."""
            self.replacement_completed = True
            if self.published_paths is not None:
                self.published_paths.append(destination)

        def cleanup(self, operation_error: BaseException) -> None:
            """Remove only authenticated staging while preserving the first cause."""
            if self.linked_temporary and self.identity is not None:
                FlextCliUtilitiesAtomicFileCleanup.remove_linked_temporary(
                    self.parent,
                    self.temporary,
                    self.identity,
                    operation_error,
                )
            elif not self.replacement_completed:
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
        staged: m.Cli.StagedFile,
    ) -> None:
        staged_state = FlextCliUtilitiesAtomicFile._validate_staged(
            parent,
            staged.path,
            staged.content,
            staged.mode,
            staged.identity,
        )
        FlextCliUtilitiesAtomicFilePublishChecks.require_distinct_inode(
            destination,
            expected,
            staged.identity,
        )
        FlextCliUtilitiesAtomicFilePublishChecks.validate_devices(
            destination,
            parent,
            parent,
            m.Cli.ObservedFile(path=staged.path, state=staged_state),
        )
        FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
            destination,
            expected,
            parent=parent,
        )
        FlextCliUtilitiesAtomicFileState.assert_temporary_owned(
            staged.path,
            staged.identity,
            parent=parent,
        )

    @staticmethod
    def _validate_staged(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        temporary: Path,
        content: bytes,
        mode: int,
        identity: tuple[int, int],
    ) -> os.stat_result:
        state = FlextCliUtilitiesAtomicFileState.file_destination_state(
            temporary,
            parent=parent,
        )
        if state is None:
            message = f"atomic temporary disappeared before publication: {temporary}"
            raise FileNotFoundError(errno.ENOENT, message, temporary)
        FlextCliUtilitiesAtomicFilePublishChecks.require_file_identity(
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
