"""Public descriptor-bound parent ownership for atomic file operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from flext_cli import t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicParentDescriptor,
    FlextCliUtilitiesAtomicParentFailure,
)


class FlextCliUtilitiesAtomicFileDescriptor:
    """Canonical namespace owner."""

    @dataclass(frozen=True, slots=True)
    class ParentDescriptor:
        """One open physical parent directory bound to its lexical pathname."""

        path: Path
        descriptor: int
        state: os.stat_result
        ancestry: t.VariadicTuple[t.Pair[int, int]]
        lineage: t.VariadicTuple[int]

    @staticmethod
    @contextmanager
    def parent_descriptor(
        path: Path,
        *,
        replace: bool = False,
        unlink: bool = False,
    ) -> Generator[ParentDescriptor]:
        """Yield one authenticated parent descriptor with required OS capabilities.

        The descriptor walk that opens the parent is itself the entry
        authentication of pathname, identity and ancestry; the pathname is
        re-walked where time has passed (before a namespace mutation, and on exit).

        Yields:
            Each ``ParentDescriptor``.

        """
        validated = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(path)
        FlextCliUtilitiesAtomicFileDescriptor._require_capabilities(
            validated,
            replace=replace,
            unlink=unlink,
        )
        with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
            validated.parent,
        ) as opened:
            handle = FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                validated.parent,
                opened.descriptor,
                opened.state,
                opened.ancestry,
                opened.lineage,
            )
            try:
                yield handle
            except BaseException as operation_error:
                FlextCliUtilitiesAtomicParentFailure.preserve_recheck_failure(
                    handle.path,
                    operation_error,
                    lambda: (
                        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(
                            handle,
                        )
                    ),
                )
                raise
            FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(handle)

    @staticmethod
    def assert_parent_unchanged(parent: ParentDescriptor) -> None:
        """Require descriptor and pathname to retain the opened directory identity.

        Raises:
            OSError: If ``file_path.identity(descriptor_state) != expected``; or if
                ``parent.ancestry[-1] != expected``.

        """
        descriptor_state = os.fstat(parent.descriptor)
        FlextCliUtilitiesAtomicFilePath.validate_directory_state(
            parent.path,
            descriptor_state,
        )
        expected = FlextCliUtilitiesAtomicFilePath.identity(parent.state)
        if FlextCliUtilitiesAtomicFilePath.identity(descriptor_state) != expected:
            message = f"atomic file parent identity changed: {parent.path}"
            raise OSError(errno.ESTALE, message, parent.path)
        if parent.ancestry[-1] != expected:
            message = f"atomic file parent ancestry changed: {parent.path}"
            raise OSError(errno.ESTALE, message, parent.path)
        FlextCliUtilitiesAtomicParentDescriptor.verify_lineage(
            parent.path,
            parent.lineage,
            parent.ancestry,
        )

    @staticmethod
    def entry_stat(parent: ParentDescriptor, path: Path) -> os.stat_result:
        """Read one final entry relative to its authenticated parent descriptor.

        Returns:
            The resulting ``os.stat_result``.

        """
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(parent, path)
        return os.stat(path.name, dir_fd=parent.descriptor, follow_symlinks=False)

    @staticmethod
    def open_entry(
        parent: ParentDescriptor,
        path: Path,
        flags: int,
        *,
        mode: int | None = None,
    ) -> int:
        """Open one final entry relative to its authenticated parent descriptor.

        Returns:
            The resulting ``int``.

        """
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(parent, path)
        nofollow_flag = getattr(os, "O_NOFOLLOW", 0)
        guarded_flags = flags | nofollow_flag
        if mode is None:
            return os.open(path.name, guarded_flags, dir_fd=parent.descriptor)
        return os.open(path.name, guarded_flags, mode, dir_fd=parent.descriptor)

    @staticmethod
    @contextmanager
    def entry_descriptor(
        parent: ParentDescriptor,
        path: Path,
        flags: int,
    ) -> Generator[int]:
        """Yield one final-entry descriptor and retain close failures causally.

        Yields:
            Each ``int``.

        """
        descriptor = FlextCliUtilitiesAtomicFileDescriptor.open_entry(
            parent,
            path,
            flags,
        )
        try:
            yield descriptor
        except BaseException as operation_error:
            FlextCliUtilitiesAtomicFileDescriptor.close_after_failure(
                descriptor,
                path,
                operation_error,
                label="operation",
            )
            raise
        os.close(descriptor)

    @staticmethod
    def unlink_entry(parent: ParentDescriptor, path: Path) -> None:
        """Unlink one entry from the still-authorized physical parent."""
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(parent, path)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
        os.unlink(path.name, dir_fd=parent.descriptor)

    @staticmethod
    def replace_entry(
        source_parent: ParentDescriptor,
        source: Path,
        destination_parent: ParentDescriptor,
        destination: Path,
    ) -> None:
        """Replace one entry using only authenticated directory descriptors."""
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(source_parent, source)
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(
            destination_parent,
            destination,
        )
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(source_parent)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(
            destination_parent,
        )
        os.replace(
            source.name,
            destination.name,
            src_dir_fd=source_parent.descriptor,
            dst_dir_fd=destination_parent.descriptor,
        )

    @staticmethod
    def _require_capabilities(path: Path, *, replace: bool, unlink: bool) -> None:
        FlextCliUtilitiesAtomicParentDescriptor.require_traversal_capabilities(path)
        operations: list[tuple[str, object]] = []
        if replace:
            # CPython exposes ``src_dir_fd``/``dst_dir_fd`` on ``os.replace`` via
            # the same renameat primitive as ``os.rename``, but records only
            # ``os.rename`` in ``supports_dir_fd`` on supported POSIX runtimes.
            operations.append(("replace", os.rename))
        if unlink:
            operations.append(("unlink", os.unlink))
        missing = [
            name
            for name, operation in operations
            if operation not in os.supports_dir_fd
        ]
        if missing:
            unsupported = sorted(set(missing))
            message = f"descriptor-bound atomic files are unsupported: {unsupported}"
            raise OSError(errno.ENOTSUP, message)

    @staticmethod
    def require_entry(parent: ParentDescriptor, path: Path) -> None:
        """Require one validated path to name a child of the opened parent.

        Raises:
            OSError: If ``validated.parent != parent.path``.

        """
        validated = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(path)
        if validated.parent != parent.path:
            message = f"atomic file does not belong to authenticated parent: {path}"
            raise OSError(errno.EINVAL, message, path)

    @staticmethod
    def close_after_failure(
        descriptor: int,
        path: Path,
        operation_error: BaseException,
        *,
        label: str,
    ) -> None:
        """Close one failed operation's descriptor, preserving causal close errors.

        Raises:
            BaseExceptionGroup: If atomic.
            OSError: If ``isinstance(operation_error, Exception)``.

        """
        try:
            os.close(descriptor)
        except OSError as close_error:
            message = (
                f"atomic {label} failed ({operation_error});"
                f" close failed ({close_error})"
            )
            group_message = f"atomic {label} and descriptor close failed"
            if isinstance(operation_error, Exception):
                causes = ExceptionGroup(group_message, [operation_error, close_error])
                raise OSError(errno.EIO, message, path) from causes
            raise BaseExceptionGroup(
                group_message,
                [operation_error, close_error],
            ) from close_error


__all__: list[str] = ["FlextCliUtilitiesAtomicFileDescriptor"]
