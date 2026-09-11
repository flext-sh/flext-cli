"""Descriptor-bound Darwin filesystem identity using the complete fsid_t."""

from __future__ import annotations

import ctypes
import errno
import os
import platform
from pathlib import Path


class FlextCliAtomicTreeDarwin:
    """Own the Darwin descriptor-bound filesystem identity contract."""

    class Statfs(ctypes.Structure):
        """Darwin's public 64-bit-inode statfs ABI (sys/mount.h)."""

        _fields_ = (
            ("f_bsize", ctypes.c_uint32),
            ("f_iosize", ctypes.c_int32),
            ("f_blocks", ctypes.c_uint64),
            ("f_bfree", ctypes.c_uint64),
            ("f_bavail", ctypes.c_uint64),
            ("f_files", ctypes.c_uint64),
            ("f_ffree", ctypes.c_uint64),
            ("f_fsid", ctypes.c_int32 * 2),
            ("f_owner", ctypes.c_uint32),
            ("f_type", ctypes.c_uint32),
            ("f_flags", ctypes.c_uint32),
            ("f_fssubtype", ctypes.c_uint32),
            ("f_fstypename", ctypes.c_char * 16),
            ("f_mntonname", ctypes.c_char * 1024),
            ("f_mntfromname", ctypes.c_char * 1024),
            ("f_flags_ext", ctypes.c_uint32),
            ("f_reserved", ctypes.c_uint32 * 7),
        )
        f_fsid: ctypes.Array[ctypes.c_int32]

    @staticmethod
    def mount_id(descriptor: int, path: Path) -> int:
        """Read both fsid words from the open FD, without resolving its pathname."""
        architecture = platform.machine()
        if architecture == "arm64":
            symbol = "fstatfs"
        elif architecture == "x86_64":
            symbol = "fstatfs$INODE64"
        else:
            message = "descriptor-bound mount identity has an unsupported Darwin ABI"
            raise OSError(errno.ENOTSUP, message, path)
        try:
            library = ctypes.CDLL(None, use_errno=True)
            operation = library[symbol]
        except (AttributeError, OSError) as exc:
            message = "Darwin libc does not expose descriptor-bound filesystem identity"
            raise OSError(errno.ENOTSUP, message, path) from exc
        operation.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(FlextCliAtomicTreeDarwin.Statfs),
        )
        operation.restype = ctypes.c_int
        state = FlextCliAtomicTreeDarwin.Statfs()
        ctypes.set_errno(0)
        if operation(descriptor, ctypes.byref(state)) != 0:
            error_number = ctypes.get_errno() or errno.EIO
            message = (
                f"descriptor-bound mount identity failed: {os.strerror(error_number)}"
            )
            raise OSError(error_number, message, path)
        value = ((state.f_fsid[0] & 0xFFFFFFFF) << 32) | (state.f_fsid[1] & 0xFFFFFFFF)
        if value == 0:
            message = "descriptor-bound mount identity must be nonzero"
            raise OSError(errno.EIO, message, path)
        return value


__all__: list[str] = ["FlextCliAtomicTreeDarwin"]
