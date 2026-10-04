"""Public stable descriptor reads for atomic file state authentication.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli import t
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)


class FlextCliUtilitiesAtomicFileRead:
    """Canonical namespace owner."""

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
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
        descriptor = FlextCliUtilitiesAtomicFileDescriptor.open_entry(
            parent, path, flags
        )
        try:
            content = FlextCliUtilitiesAtomicFileRead._read_stable_descriptor(
                descriptor, path, expected
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
    def _read_stable_descriptor(
        descriptor: int,
        path: Path,
        expected: os.stat_result,
    ) -> bytes:
        if FlextCliUtilitiesAtomicFileRead.state_key(
            os.fstat(descriptor)
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicFileRead._raise_changed(path)
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        if FlextCliUtilitiesAtomicFileRead.state_key(
            os.fstat(descriptor)
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicFileRead._raise_changed(path)
        return b"".join(chunks)

    @staticmethod
    def _raise_changed(path: Path) -> None:
        message = f"atomic destination changed during authenticated read: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileRead"]
