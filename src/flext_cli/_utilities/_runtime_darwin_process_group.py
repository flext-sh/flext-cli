"""Darwin process-group membership, including members awaiting reaping."""

from __future__ import annotations

import ctypes
import errno
import os


class FlextCliUtilitiesRuntimeDarwinProcessGroupMixin:
    """Read libproc rather than treating killpg permission as membership."""

    @staticmethod
    def _darwin_process_group_members(process_group_id: int) -> tuple[int, ...]:
        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        list_pids = library.proc_listpgrppids
        list_pids.argtypes = (ctypes.c_int, ctypes.c_void_p, ctypes.c_int)
        list_pids.restype = ctypes.c_int
        capacity = int(list_pids(process_group_id, None, 0))
        if capacity <= 0:
            error = ctypes.get_errno()
            raise OSError(
                error, f"proc_listpgrppids sizing failed: {os.strerror(error)}"
            )
        while True:
            buffer = (ctypes.c_int * capacity)()
            ctypes.set_errno(0)
            count = int(list_pids(process_group_id, buffer, ctypes.sizeof(buffer)))
            error = ctypes.get_errno()
            if count < 0 or (count == 0 and error):
                raise OSError(error, f"proc_listpgrppids failed: {os.strerror(error)}")
            if count < capacity:
                return tuple(buffer[:count])
            capacity *= 2

    @classmethod
    def _darwin_process_group_exited(cls, process_group_id: int) -> bool:
        """Prove EPERM came from an empty/zombie group, never deny a live member."""

        class _BsdShortInfo(ctypes.Structure):
            _fields_ = [
                ("pid", ctypes.c_uint32),
                ("ppid", ctypes.c_uint32),
                ("pgid", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("comm", ctypes.c_char * 16),
                ("flags", ctypes.c_uint32),
                ("uid", ctypes.c_uint32),
                ("gid", ctypes.c_uint32),
                ("ruid", ctypes.c_uint32),
                ("rgid", ctypes.c_uint32),
                ("svuid", ctypes.c_uint32),
                ("svgid", ctypes.c_uint32),
                ("reserved", ctypes.c_uint32),
            ]

        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        pid_info = library.proc_pidinfo
        pid_info.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_int,
        )
        pid_info.restype = ctypes.c_int
        zombie_status = 5  # SZOMB in the Darwin sys/proc.h ABI.
        for process_id in cls._darwin_process_group_members(process_group_id):
            info = _BsdShortInfo()
            ctypes.set_errno(0)
            size = int(
                pid_info(process_id, 13, 0, ctypes.byref(info), ctypes.sizeof(info))
            )
            error = ctypes.get_errno()
            if size == 0 and error == errno.ESRCH:
                continue
            if size != ctypes.sizeof(info):
                raise OSError(error, f"proc_pidinfo failed for {process_id}: {size}")
            if info.pgid == process_group_id and info.status != zombie_status:
                return False
        return True


__all__: list[str] = ["FlextCliUtilitiesRuntimeDarwinProcessGroupMixin"]
