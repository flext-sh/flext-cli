"""Platform owner for descriptor-bound, no-clobber directory rename.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import ctypes
import errno
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast

from flext_cli.typings import RenameAt2

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesAtomicDirectoryNoreplace:
    """Canonical namespace owner."""

    _RENAME_NOREPLACE: ClassVar[int] = 1

    _RENAME_EXCL: ClassVar[int] = 4

    @staticmethod
    def require_noreplace_capability(path: Path) -> None:
        """Fail before effects unless this host has a real no-replace primitive.

        Raises:
            OSError: Always.

        """
        platform_name, os_name = (
            FlextCliUtilitiesAtomicDirectoryNoreplace._runtime_platform()
        )
        if platform_name == "linux":
            _ = FlextCliUtilitiesAtomicDirectoryNoreplace._linux_renameat2(path)
            return
        if platform_name == "darwin":
            _ = FlextCliUtilitiesAtomicDirectoryNoreplace._darwin_renameatx(path)
            return
        if os_name == "nt" and os.rename in os.supports_dir_fd:
            return
        message = "descriptor-bound no-replace directory rename is unsupported"
        raise OSError(errno.ENOTSUP, message, path)

    @staticmethod
    def rename_noreplace(
        source_descriptor: int,
        source_name: str,
        destination_descriptor: int,
        destination_name: str,
        *,
        path: Path,
    ) -> None:
        """Rename one relative entry without replacing an existing destination.

        Raises:
            OSError: Always; or if ``result != 0``.

        """
        source_bytes = FlextCliUtilitiesAtomicDirectoryNoreplace._encode_name(
            source_name,
            path,
        )
        destination_bytes = FlextCliUtilitiesAtomicDirectoryNoreplace._encode_name(
            destination_name,
            path,
        )
        platform_name, os_name = (
            FlextCliUtilitiesAtomicDirectoryNoreplace._runtime_platform()
        )
        if platform_name in {"linux", "darwin"}:
            if platform_name == "linux":
                operation = FlextCliUtilitiesAtomicDirectoryNoreplace._linux_renameat2(
                    path,
                )
                flags = FlextCliUtilitiesAtomicDirectoryNoreplace._RENAME_NOREPLACE
            else:
                operation = FlextCliUtilitiesAtomicDirectoryNoreplace._darwin_renameatx(
                    path,
                )
                flags = FlextCliUtilitiesAtomicDirectoryNoreplace._RENAME_EXCL
            ctypes.set_errno(0)
            result = operation(
                source_descriptor,
                source_bytes,
                destination_descriptor,
                destination_bytes,
                flags,
            )
            if result != 0:
                error_number = ctypes.get_errno() or errno.EIO
                message = (
                    f"no-replace directory rename failed: {os.strerror(error_number)}"
                )
                raise OSError(error_number, message, path)
            return
        if os_name == "nt" and os.rename in os.supports_dir_fd:
            os.rename(
                source_name,
                destination_name,
                src_dir_fd=source_descriptor,
                dst_dir_fd=destination_descriptor,
            )
            return
        message = "descriptor-bound no-replace directory rename is unsupported"
        raise OSError(errno.ENOTSUP, message, path)

    @staticmethod
    def _runtime_platform() -> t.Pair[str, str]:
        """Read host selectors at invocation time for portable typed dispatch.

        Returns:
            The resulting ``t.Pair[str, str]``.

        """
        return sys.platform, os.name

    @staticmethod
    def _linux_renameat2(path: Path) -> RenameAt2:
        return FlextCliUtilitiesAtomicDirectoryNoreplace._load_rename(
            "renameat2",
            "Linux",
            path,
        )

    @staticmethod
    def _darwin_renameatx(path: Path) -> RenameAt2:
        """Load Apple's descriptor-relative exclusive rename, never plain rename.

        Returns:
            The resulting ``RenameAt2``.

        """
        return FlextCliUtilitiesAtomicDirectoryNoreplace._load_rename(
            "renameatx_np",
            "Darwin",
            path,
        )

    @staticmethod
    def _load_rename(symbol: str, platform_name: str, path: Path) -> RenameAt2:
        try:
            library = ctypes.CDLL(None, use_errno=True)
            operation = library[symbol]
        except (AttributeError, OSError) as exc:
            message = f"{platform_name} libc does not expose {symbol}"
            raise OSError(errno.ENOTSUP, message, path) from exc
        operation.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        operation.restype = ctypes.c_int
        return cast("RenameAt2", operation)

    @staticmethod
    def _encode_name(name: str, path: Path) -> bytes:
        encoded = os.fsencode(name)
        if b"\0" in encoded:
            message = "atomic directory name contains a null byte"
            raise OSError(errno.EINVAL, message, path)
        return encoded


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryNoreplace"]
