"""Public stable descriptor reads for atomic file state authentication.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import hashlib
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from flext_cli import m, p, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileModel,
    FlextCliUtilitiesAtomicFileSnapshot,
)


class FlextCliUtilitiesAtomicFileRead:
    """Canonical namespace owner."""

    READ_FLAGS = (
        os.O_RDONLY
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )

    class Reader:
        """One scoped descriptor serving ranges of an authenticated version."""

        def __init__(
            self, descriptor: int, path: Path, expected: os.stat_result
        ) -> None:
            self.descriptor = descriptor
            self.path = path
            self.expected = expected

        def read_range(self, offset: int, length: int) -> bytes:
            """Read the complete requested range, refusing mutation or short reads."""
            if (
                isinstance(offset, bool)
                or isinstance(length, bool)
                or offset < 0
                or length < 0
                or offset + length > self.expected.st_size
            ):
                raise ValueError("atomic range lies outside the authenticated file")
            if FlextCliUtilitiesAtomicFileRead.state_key(
                os.fstat(self.descriptor)
            ) != FlextCliUtilitiesAtomicFileRead.state_key(self.expected):
                FlextCliUtilitiesAtomicFileRead._raise_changed(self.path)
            os.lseek(self.descriptor, offset, os.SEEK_SET)
            remaining = length
            chunks: list[bytes] = []
            while remaining:
                chunk = os.read(self.descriptor, min(remaining, 1024 * 1024))
                if not chunk:
                    FlextCliUtilitiesAtomicFileRead._raise_changed(self.path)
                chunks.append(chunk)
                remaining -= len(chunk)
            if FlextCliUtilitiesAtomicFileRead.state_key(
                os.fstat(self.descriptor)
            ) != FlextCliUtilitiesAtomicFileRead.state_key(self.expected):
                FlextCliUtilitiesAtomicFileRead._raise_changed(self.path)
            return b"".join(chunks)

    @staticmethod
    def read_receipt(
        path: Path,
        *,
        required: bool,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> m.Cli.AtomicFileReceipt:
        """Measure exact bytes once while retaining descriptor and parent identity."""
        with FlextCliUtilitiesAtomicFileSnapshot.authenticated_entry(
            path, required=required, owner_uid=owner_uid, max_bytes=max_bytes
        ) as (parent, state):
            if parent is None or state is None:
                return m.Cli.AtomicFileReceipt(
                    path=path,
                    parent_device=None if parent is None else parent.state.st_dev,
                    parent_inode=None if parent is None else parent.state.st_ino,
                )
            with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                parent, path, FlextCliUtilitiesAtomicFileRead.READ_FLAGS
            ) as descriptor:
                digest = hashlib.sha256()
                size = 0
                for chunk in FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                    descriptor, path, state
                ):
                    digest.update(chunk)
                    size += len(chunk)
                return m.Cli.AtomicFileReceipt(
                    path=path,
                    parent_device=parent.state.st_dev,
                    parent_inode=parent.state.st_ino,
                    mode=stat.S_IMODE(state.st_mode),
                    device=state.st_dev,
                    inode=state.st_ino,
                    link_count=state.st_nlink,
                    file_attributes=getattr(state, "st_file_attributes", None),
                    reparse_tag=getattr(state, "st_reparse_tag", None),
                    size=size,
                    sha256=digest.hexdigest(),
                    version_key=FlextCliUtilitiesAtomicFileRead.state_key(state),
                )

    @staticmethod
    @contextmanager
    def receipt_reader(receipt: m.Cli.AtomicFileReceipt) -> Iterator[p.Cli.AtomicFileReader]:
        """Authenticate a receipt once and retain one descriptor for all ranges."""
        with FlextCliUtilitiesAtomicFileSnapshot.authenticated_entry(
            receipt.path, required=True
        ) as (parent, state):
            if parent is None or state is None:
                raise FileNotFoundError(errno.ENOENT, "missing receipt file", receipt.path)
            FlextCliUtilitiesAtomicFileModel.require_parent(receipt, parent.state)
            if (
                receipt.version_key != FlextCliUtilitiesAtomicFileRead.state_key(state)
                or receipt.size != state.st_size
            ):
                FlextCliUtilitiesAtomicFileRead._raise_changed(receipt.path)
            with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                parent, receipt.path, FlextCliUtilitiesAtomicFileRead.READ_FLAGS
            ) as descriptor:
                digest = hashlib.sha256()
                for chunk in FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                    descriptor, receipt.path, state
                ):
                    digest.update(chunk)
                if digest.hexdigest() != receipt.sha256:
                    FlextCliUtilitiesAtomicFileRead._raise_changed(receipt.path)
                yield FlextCliUtilitiesAtomicFileRead.Reader(descriptor, receipt.path, state)
                if FlextCliUtilitiesAtomicFileRead.state_key(
                    os.fstat(descriptor)
                ) != receipt.version_key:
                    FlextCliUtilitiesAtomicFileRead._raise_changed(receipt.path)

    @staticmethod
    def read_descriptor_bytes(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        expected: os.stat_result,
    ) -> bytes:
        """Read all bytes while one descriptor retains the expected exact state.

        Returns:
            The resulting ``bytes``.

        """
        descriptor = FlextCliUtilitiesAtomicFileDescriptor.open_entry(
            parent,
            path,
            FlextCliUtilitiesAtomicFileRead.READ_FLAGS,
        )
        try:
            content = b"".join(
                FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                    descriptor, path, expected
                )
            )
        except BaseException as operation_error:
            FlextCliUtilitiesAtomicFileDescriptor.close_after_failure(
                descriptor,
                path,
                operation_error,
                label="read",
            )
            raise
        os.close(descriptor)
        return content

    @staticmethod
    def state_key(state: os.stat_result) -> t.VariadicTuple[int]:
        """Return fields that identify one authorized regular-file version.

        Returns:
            Fields that identify one authorized regular-file version.

        """
        return (
            state.st_dev,
            state.st_ino,
            state.st_mode,
            state.st_nlink,
            state.st_uid,
            state.st_gid,
            state.st_size,
            state.st_mtime_ns,
            state.st_ctime_ns,
            getattr(state, "st_file_attributes", 0),
            getattr(state, "st_reparse_tag", 0),
        )

    @staticmethod
    def descriptor_chunks(
        descriptor: int,
        path: Path,
        expected: os.stat_result,
    ) -> t.IterableOf[bytes]:
        """Consume exact chunks between checks of the authenticated file version.

        Yields:
            Each ``bytes`` chunk read from the authenticated descriptor.

        """
        if FlextCliUtilitiesAtomicFileRead.state_key(
            os.fstat(descriptor),
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicFileRead._raise_changed(path)
        while chunk := os.read(descriptor, 1024 * 1024):
            yield chunk
        if FlextCliUtilitiesAtomicFileRead.state_key(
            os.fstat(descriptor),
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicFileRead._raise_changed(path)

    @staticmethod
    def _raise_changed(path: Path) -> None:
        message = f"atomic destination changed during authenticated read: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileRead"]
