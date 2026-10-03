"""Public descriptor-owned staging for one atomic file replacement.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import secrets
import stat
from pathlib import Path
from typing import ClassVar

from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_mode import FlextCliUtilitiesAtomicFileMode


class FlextCliUtilitiesAtomicFileTemporary:
    """Canonical namespace owner."""

    _SECURE_CREATE_MODE: ClassVar[int] = 0o600

    @staticmethod
    def temporary_path(
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
    ) -> Path:
        """Return one unpredictable sibling name without probing or retrying.

        Returns:
            One unpredictable sibling name without probing or retrying.

        """
        return parent.path / f".flext-atomic-{secrets.token_hex(16)}.tmp"

    @staticmethod
    def require_mode_capability(path: Path, permission_mode: int | None) -> None:
        """Fail before staging if an exact requested mode cannot use its descriptor.

        Raises:
            OSError: If ``permission_mode is not None and os.chmod not in os.supports_fd``.

        """
        if permission_mode is not None and os.chmod not in os.supports_fd:
            message = "descriptor permission changes are unsupported"
            raise OSError(errno.ENOTSUP, message, path)

    @staticmethod
    def create_descriptor(
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        temporary: Path,
    ) -> int:
        """Create one exclusive, securely permissioned sibling through ``dir_fd``.

        Returns:
            The resulting ``int``.

        """
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
        )
        return FlextCliUtilitiesAtomicFileDescriptor.open_entry(
            parent,
            temporary,
            flags,
            mode=FlextCliUtilitiesAtomicFileTemporary._SECURE_CREATE_MODE,
        )

    @staticmethod
    def write_and_sync(
        descriptor: int,
        temporary: Path,
        content: bytes,
        permission_mode: int | None,
    ) -> int:
        """Write exact bytes, materialize exact mode, and sync the open inode.

        Returns:
            The resulting ``int``.

        Raises:
            OSError: If ``written == 0``.

        """
        remaining = memoryview(content)
        while remaining:
            written = os.write(descriptor, remaining)
            if written == 0:
                message = f"atomic temporary write made no progress: {temporary}"
                raise OSError(errno.EIO, message, temporary)
            remaining = remaining[written:]
        if permission_mode is not None:
            os.chmod(descriptor, permission_mode)
            FlextCliUtilitiesAtomicFileMode.assert_observed_mode(
                temporary, os.fstat(descriptor), permission_mode
            )
        os.fsync(descriptor)
        return stat.S_IMODE(os.fstat(descriptor).st_mode)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileTemporary"]
