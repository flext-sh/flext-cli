"""Public stable descriptor reads for atomic file state authentication.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from flext_cli._utilities import FlextCliUtilitiesAtomicFileDescriptor


class FlextCliUtilitiesAtomicFileRead:
    """Canonical namespace owner."""

    READ_FLAGS: ClassVar[int] = (
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
            self.version_key = FlextCliUtilitiesAtomicFileRead.state_key(expected)

        def read_range(self, offset: int, length: int) -> bytes:
            """Read the complete requested range, refusing mutation or short reads.

            Returns:
                The exact bytes of the requested range from the authenticated
                version.

            Raises:
                ValueError: If the requested range lies outside the
                    authenticated file.

            """
            integral = not isinstance(offset, bool) and not isinstance(length, bool)
            if (
                not integral
                or offset < 0
                or length < 0
                or offset + length > self.expected.st_size
            ):
                msg = "atomic range lies outside the authenticated file"
                raise ValueError(msg)
            observed = FlextCliUtilitiesAtomicFileRead.state_key(
                os.fstat(self.descriptor)
            )
            if observed != self.version_key:
                FlextCliUtilitiesAtomicFileRead.raise_changed(
                    self.path, self.version_key, observed
                )
            os.lseek(self.descriptor, offset, os.SEEK_SET)
            remaining = length
            chunks: list[bytes] = []
            while remaining:
                chunk = os.read(self.descriptor, min(remaining, 1024 * 1024))
                if not chunk:
                    FlextCliUtilitiesAtomicFileRead.raise_changed(self.path)
                chunks.append(chunk)
                remaining -= len(chunk)
            observed = FlextCliUtilitiesAtomicFileRead.state_key(
                os.fstat(self.descriptor)
            )
            if observed != self.version_key:
                FlextCliUtilitiesAtomicFileRead.raise_changed(
                    self.path, self.version_key, observed
                )
            return b"".join(chunks)

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

    # Names of the ``state_key`` fields, in its order.
    STATE_KEY_FIELDS: ClassVar[tuple[str, ...]] = (
        "st_dev",
        "st_ino",
        "st_mode",
        "st_nlink",
        "st_uid",
        "st_gid",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
        "st_file_attributes",
        "st_reparse_tag",
    )

    @staticmethod
    def state_key(state: os.stat_result) -> tuple[int, ...]:
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
    ) -> Iterable[bytes]:
        """Consume exact chunks between checks of the authenticated file version.

        Yields:
            Each ``bytes`` chunk read from the authenticated descriptor.

        """
        observed = FlextCliUtilitiesAtomicFileRead.state_key(os.fstat(descriptor))
        if observed != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicFileRead.raise_changed(
                path, FlextCliUtilitiesAtomicFileRead.state_key(expected), observed
            )
        os.lseek(descriptor, 0, os.SEEK_SET)
        size = 0
        while chunk := os.read(descriptor, 1024 * 1024):
            size += len(chunk)
            if size > expected.st_size:
                FlextCliUtilitiesAtomicFileRead.raise_changed(path)
            yield chunk
        if size != expected.st_size:
            FlextCliUtilitiesAtomicFileRead.raise_changed(path)
        observed = FlextCliUtilitiesAtomicFileRead.state_key(os.fstat(descriptor))
        if observed != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicFileRead.raise_changed(
                path, FlextCliUtilitiesAtomicFileRead.state_key(expected), observed
            )

    @staticmethod
    def raise_changed(
        path: Path,
        expected: tuple[int, ...] | None = None,
        observed: tuple[int, ...] | None = None,
    ) -> None:
        """Reject a changed authenticated version at the read boundary.

        Given both version keys, the refusal names every field that differs
        with its expected and observed value, so the cause of a recurrence is
        read from the message instead of inferred.

        Raises:
            OSError: Unconditionally, with ``errno.ESTALE`` naming the changed
                authenticated destination and, when known, its changed fields.

        """
        message = f"atomic destination changed during authenticated read: {path}"
        if expected is not None and observed is not None:
            changed = ", ".join(
                f"{name} {before} -> {after}"
                for name, before, after in zip(
                    FlextCliUtilitiesAtomicFileRead.STATE_KEY_FIELDS,
                    expected,
                    observed,
                    strict=True,
                )
                if before != after
            )
            message = f"{message} (changed: {changed or 'none'})"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileRead"]
