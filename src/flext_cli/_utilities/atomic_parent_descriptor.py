"""Component-authenticated physical directory descriptor traversal.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from flext_cli import t
from flext_cli._utilities import FlextCliUtilitiesAtomicFilePath
from flext_cli.typings import DirectoryChainInspection


class FlextCliUtilitiesAtomicParentDescriptor:
    """Canonical namespace owner."""

    @dataclass(frozen=True, slots=True)
    class PhysicalDirectory:
        """One descriptor, the exact ancestry used to reach it, and its held lineage.

        ``lineage`` holds one open descriptor per proper ancestor, root first,
        aligned with ``ancestry[:-1]``; it stays open for the context's lifetime so
        the pathname can be re-authenticated relative to each held ancestor.
        """

        descriptor: int
        state: os.stat_result
        ancestry: t.VariadicTuple[t.Pair[int, int]]
        lineage: t.VariadicTuple[int]

    @staticmethod
    @contextmanager
    def physical_directory(path: Path) -> Generator[PhysicalDirectory]:
        """Open an absolute directory one non-aliased component at a time.

        The descriptor walk is the only traversal: each component is stat'ed
        without following links relative to its already-authenticated parent
        descriptor, opened with ``O_NOFOLLOW``, and its descriptor identity must
        equal that stat. A missing or aliased component fails with the same
        verdict and component path a separate lexical pre-pass would report.

        Yields:
            Each ``PhysicalDirectory``.

        """
        FlextCliUtilitiesAtomicParentDescriptor.require_traversal_capabilities(path)
        FlextCliUtilitiesAtomicFilePath.validate_directory_path(path)
        descriptors: list[int] = []
        try:
            descriptor, state, ancestry, _consumed = (
                FlextCliUtilitiesAtomicParentDescriptor._open_components(
                    path,
                    descriptors,
                    stop_at_missing=False,
                )
            )
        except BaseException as operation_error:
            FlextCliUtilitiesAtomicParentDescriptor._close_after_failure(
                descriptors,
                path,
                operation_error,
            )
            raise
        opened = FlextCliUtilitiesAtomicParentDescriptor.PhysicalDirectory(
            descriptor,
            state,
            ancestry,
            tuple(descriptors[:-1]),
        )
        try:
            yield opened
        except BaseException as operation_error:
            FlextCliUtilitiesAtomicParentDescriptor._close_after_failure(
                descriptors,
                path,
                operation_error,
            )
            raise
        FlextCliUtilitiesAtomicParentDescriptor._close_descriptors(descriptors, path)

    @staticmethod
    def verify_lineage(
        path: Path,
        lineage: t.VariadicTuple[int],
        ancestry: t.VariadicTuple[t.Pair[int, int]],
    ) -> None:
        """Prove ``path`` still resolves, component by component, to ``ancestry``.

        Each component is stat'ed without following links relative to its held
        ancestor descriptor, which is exactly what a fresh walk from the root
        observes at that instant: a missing, aliased, replaced or renamed ancestor
        fails with the same verdict a re-walk reports, without reopening the chain.

        Raises:
            FileNotFoundError: If a ``FileNotFoundError`` is caught.
            OSError: If ``len(parts) != len(ancestry) or len(lineage) != len(ancestry) -
                1``; or if ``file_path.identity(root_state) != ancestry[0]``; or if
                ``file_path.identity(state) != ancestry[index + 1]``.

        """
        parts = path.parts
        if len(parts) != len(ancestry) or len(lineage) != len(ancestry) - 1:
            message = f"atomic parent lineage does not match its pathname: {path}"
            raise OSError(errno.EINVAL, message, path)
        root = Path(path.anchor)
        root_state = root.lstat()
        FlextCliUtilitiesAtomicFilePath.validate_directory_state(root, root_state)
        if FlextCliUtilitiesAtomicFilePath.identity(root_state) != ancestry[0]:
            message = f"atomic file parent ancestry changed: {path}"
            raise OSError(errno.ESTALE, message, path)
        for index, holder in enumerate(lineage):
            component = parts[index + 1]
            try:
                state = os.stat(component, dir_fd=holder, follow_symlinks=False)
            except FileNotFoundError as missing:
                absent = root.joinpath(*parts[1 : index + 2])
                message = f"atomic destination parent is missing: {absent}"
                raise FileNotFoundError(errno.ENOENT, message, absent) from missing
            if not stat.S_ISDIR(
                state.st_mode,
            ) or FlextCliUtilitiesAtomicFilePath.reparse_point(state):
                FlextCliUtilitiesAtomicFilePath.validate_directory_state(
                    root.joinpath(*parts[1 : index + 2]),
                    state,
                )
            if FlextCliUtilitiesAtomicFilePath.identity(state) != ancestry[index + 1]:
                message = f"atomic file parent ancestry changed: {path}"
                raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def inspect_directory_chain(path: Path) -> DirectoryChainInspection:
        """Find the exact existing anchor and every contiguous missing directory.

        Returns:
            The resulting ``DirectoryChainInspection``.

        Raises:
            OSError: If ``current.ancestry != ancestry or
                file_path.identity(current.state)
                != (state.st_dev, state.st_ino)``.

        """
        target = FlextCliUtilitiesAtomicFilePath.validate_directory_path(path)
        FlextCliUtilitiesAtomicParentDescriptor.require_traversal_capabilities(target)
        descriptors: list[int] = []
        try:
            _descriptor, state, ancestry, consumed = (
                FlextCliUtilitiesAtomicParentDescriptor._open_components(
                    target,
                    descriptors,
                    stop_at_missing=True,
                )
            )
            parts = target.relative_to(Path(target.anchor)).parts
            anchor = Path(target.anchor).joinpath(*parts[:consumed])
            missing = FlextCliUtilitiesAtomicParentDescriptor._missing_paths(
                anchor,
                parts[consumed:],
            )
            FlextCliUtilitiesAtomicParentDescriptor._close_descriptors(
                descriptors,
                target,
            )
        except BaseException as operation_error:
            FlextCliUtilitiesAtomicParentDescriptor._close_after_failure(
                descriptors,
                target,
                operation_error,
            )
            raise
        with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
            anchor,
        ) as current:
            if current.ancestry != ancestry or FlextCliUtilitiesAtomicFilePath.identity(
                current.state,
            ) != (
                state.st_dev,
                state.st_ino,
            ):
                message = f"atomic directory-chain anchor changed: {anchor}"
                raise OSError(errno.ESTALE, message, anchor)
        return anchor, state, ancestry, missing

    @staticmethod
    def require_traversal_capabilities(path: Path) -> None:
        """Require the descriptor and no-follow operations used for path traversal.

        Raises:
            OSError: If ``missing``.

        """
        missing = [
            name
            for name, operation in (("open", os.open), ("stat", os.stat))
            if operation not in os.supports_dir_fd
        ]
        if os.stat not in os.supports_follow_symlinks:
            missing.append("stat(follow_symlinks=False)")
        if not getattr(os, "O_DIRECTORY", 0):
            missing.append("O_DIRECTORY")
        if not getattr(os, "O_NOFOLLOW", 0):
            missing.append("O_NOFOLLOW")
        if missing:
            unsupported = sorted(set(missing))
            message = f"descriptor-bound path traversal is unsupported: {unsupported}"
            raise OSError(errno.ENOTSUP, message, path)

    @staticmethod
    def _open_components(
        path: Path,
        descriptors: list[int],
        *,
        stop_at_missing: bool,
    ) -> t.Quad[int, os.stat_result, t.VariadicTuple[t.Pair[int, int]], int]:
        flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
        )
        root = Path(path.anchor)
        descriptor = os.open(root, flags)
        descriptors.append(descriptor)
        state = os.fstat(descriptor)
        FlextCliUtilitiesAtomicFilePath.validate_directory_state(root, state)
        ancestry: list[tuple[int, int]] = [
            FlextCliUtilitiesAtomicFilePath.identity(state),
        ]
        parts = path.relative_to(root).parts
        for index, component in enumerate(parts):
            try:
                relative_state = os.stat(
                    component,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError as missing:
                if stop_at_missing:
                    return descriptor, state, tuple(ancestry), index
                absent = root.joinpath(*parts[: index + 1])
                message = f"atomic destination parent is missing: {absent}"
                raise FileNotFoundError(errno.ENOENT, message, absent) from missing
            if not stat.S_ISDIR(
                relative_state.st_mode,
            ) or FlextCliUtilitiesAtomicFilePath.reparse_point(
                relative_state,
            ):
                FlextCliUtilitiesAtomicFilePath.validate_directory_state(
                    root.joinpath(*parts[: index + 1]),
                    relative_state,
                )
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            descriptors.append(next_descriptor)
            descriptor_state = os.fstat(next_descriptor)
            FlextCliUtilitiesAtomicFilePath.validate_directory_state(
                path,
                descriptor_state,
            )
            if FlextCliUtilitiesAtomicFilePath.identity(
                relative_state,
            ) != FlextCliUtilitiesAtomicFilePath.identity(descriptor_state):
                message = f"atomic parent component identity changed: {path}"
                raise OSError(errno.ESTALE, message, path)
            descriptor = next_descriptor
            state = descriptor_state
            ancestry.append(FlextCliUtilitiesAtomicFilePath.identity(state))
        return descriptor, state, tuple(ancestry), len(parts)

    @staticmethod
    def _missing_paths(
        anchor: Path,
        parts: t.VariadicTuple[str],
    ) -> t.VariadicTuple[Path]:
        missing: list[Path] = []
        current = anchor
        for component in parts:
            current /= component
            missing.append(current)
        return tuple(missing)

    @staticmethod
    def _close_descriptors(descriptors: list[int], path: Path) -> None:
        close_errors: list[OSError] = []
        while descriptors:
            try:
                os.close(descriptors.pop())
            except OSError as close_error:
                close_errors.append(close_error)
        if close_errors:
            message = "; ".join(str(error) for error in close_errors)
            raise OSError(errno.EIO, f"atomic descriptor close failed: {message}", path)

    @staticmethod
    def _close_after_failure(
        descriptors: list[int],
        path: Path,
        operation_error: BaseException,
    ) -> None:
        try:
            FlextCliUtilitiesAtomicParentDescriptor._close_descriptors(
                descriptors,
                path,
            )
        except OSError as close_error:
            message = f"atomic operation failed ({operation_error}); {close_error}"
            if isinstance(operation_error, Exception):
                causes = ExceptionGroup(
                    "atomic operation and descriptor close failed",
                    [operation_error, close_error],
                )
                raise OSError(errno.EIO, message, path) from causes
            group_message = "atomic operation and descriptor close failed"
            raise BaseExceptionGroup(
                group_message,
                [operation_error, close_error],
            ) from close_error


__all__: list[str] = ["FlextCliUtilitiesAtomicParentDescriptor"]
