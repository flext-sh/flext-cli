"""Platform owner for descriptor-bound, no-clobber directory rename."""

from __future__ import annotations

import ctypes
import errno
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

type RenameAt2 = Callable[[int, bytes, int, bytes, int], int]

_RENAME_NOREPLACE = 1
_RENAME_EXCL = 4


def require_noreplace_capability(path: Path) -> None:
    """Fail before effects unless this host has a real no-replace primitive."""
    platform_name, os_name = _runtime_platform()
    if platform_name == "linux":
        _ = _linux_renameat2(path)
        return
    if platform_name == "darwin":
        _ = _darwin_renameatx(path)
        return
    if os_name == "nt" and os.rename in os.supports_dir_fd:
        return
    message = "descriptor-bound no-replace directory rename is unsupported"
    raise OSError(errno.ENOTSUP, message, path)


def rename_noreplace(
    source_descriptor: int,
    source_name: str,
    destination_descriptor: int,
    destination_name: str,
    *,
    path: Path,
) -> None:
    """Rename one relative entry without replacing an existing destination."""
    source_bytes = _encode_name(source_name, path)
    destination_bytes = _encode_name(destination_name, path)
    platform_name, os_name = _runtime_platform()
    if platform_name in {"linux", "darwin"}:
        if platform_name == "linux":
            operation = _linux_renameat2(path)
            flags = _RENAME_NOREPLACE
        else:
            operation = _darwin_renameatx(path)
            flags = _RENAME_EXCL
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
            message = f"no-replace directory rename failed: {os.strerror(error_number)}"
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


def _runtime_platform() -> tuple[str, str]:
    """Read host selectors at invocation time for portable typed dispatch."""
    return sys.platform, os.name


def _linux_renameat2(path: Path) -> RenameAt2:
    return _load_rename("renameat2", path)


def _darwin_renameatx(path: Path) -> RenameAt2:
    """Load Apple's descriptor-relative exclusive rename, never plain rename."""
    return _load_rename("renameatx_np", path)


def _load_rename(symbol: str, path: Path) -> RenameAt2:
    try:
        library = ctypes.CDLL(None, use_errno=True)
        operation = library[symbol]
    except (AttributeError, OSError) as exc:
        message = f"host libc does not expose {symbol}"
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


def _encode_name(name: str, path: Path) -> bytes:
    encoded = os.fsencode(name)
    if b"\0" in encoded:
        message = "atomic directory name contains a null byte"
        raise OSError(errno.EINVAL, message, path)
    return encoded


__all__: list[str] = ["rename_noreplace", "require_noreplace_capability"]
