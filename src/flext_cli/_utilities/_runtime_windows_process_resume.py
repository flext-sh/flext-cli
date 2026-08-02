"""Windows suspended-process resume after Job Object containment."""

from __future__ import annotations

import os


class FlextCliUtilitiesRuntimeWindowsProcessResumeMixin:
    """Resume the initial Windows thread only after Job assignment."""

    @classmethod
    def _windows_process_resume(cls, process_id: int) -> str | None:
        """Resume the initial thread and close every temporary handle."""
        if os.name != "nt":
            return None
        try:
            return cls._windows_process_resume_native(process_id)
        except (OSError, TypeError, ValueError) as exc:
            return f"Windows process resume error: {exc}"

    @classmethod
    def _windows_process_resume_native(cls, process_id: int) -> str | None:
        """Resume one Windows process after native API setup."""
        import ctypes
        from ctypes import wintypes

        class _ThreadEntry32(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ThreadID", wintypes.DWORD),
                ("th32OwnerProcessID", wintypes.DWORD),
                ("tpBasePri", wintypes.LONG),
                ("tpDeltaPri", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_snapshot = kernel32.CreateToolhelp32Snapshot
        create_snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
        create_snapshot.restype = wintypes.HANDLE
        thread_first = kernel32.Thread32First
        thread_first.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(_ThreadEntry32),
        )
        thread_first.restype = wintypes.BOOL
        thread_next = kernel32.Thread32Next
        thread_next.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(_ThreadEntry32),
        )
        thread_next.restype = wintypes.BOOL
        open_thread = kernel32.OpenThread
        open_thread.argtypes = (
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        )
        open_thread.restype = wintypes.HANDLE
        resume_thread = kernel32.ResumeThread
        resume_thread.argtypes = (wintypes.HANDLE,)
        resume_thread.restype = wintypes.DWORD
        snapshot = create_snapshot(0x00000004, 0)
        snapshot_error = ctypes.get_last_error()
        if not snapshot or snapshot == ctypes.c_void_p(-1).value:
            return f"CreateToolhelp32Snapshot failed: {snapshot_error}"
        entry = _ThreadEntry32()
        entry.dwSize = ctypes.sizeof(entry)
        thread_id = 0
        enumeration_error: int | None = None
        try:
            found = bool(thread_first(snapshot, ctypes.byref(entry)))
            first_error = ctypes.get_last_error()
            if not found and first_error not in (0, 18):
                enumeration_error = first_error
            while found:
                if entry.th32OwnerProcessID == process_id:
                    thread_id = int(entry.th32ThreadID)
                    break
                found = bool(thread_next(snapshot, ctypes.byref(entry)))
                next_error = ctypes.get_last_error()
                if not found and next_error not in (0, 18):
                    enumeration_error = next_error
        finally:
            snapshot_close_error = cls._windows_close_startup_handle(
                int(snapshot)
            )
        if enumeration_error is not None:
            detail = (
                f"; {snapshot_close_error}"
                if snapshot_close_error is not None
                else ""
            )
            return f"Windows thread enumeration failed: {enumeration_error}{detail}"
        if snapshot_close_error is not None:
            return snapshot_close_error
        if thread_id == 0:
            return (
                "Windows thread enumeration completed without a thread for "
                f"suspended process {process_id}"
            )
        thread_handle = open_thread(0x0002, False, thread_id)
        open_error = ctypes.get_last_error()
        if not thread_handle:
            return f"OpenThread failed: {open_error}"
        try:
            prior_suspend_count = resume_thread(thread_handle)
            resume_error = ctypes.get_last_error()
        finally:
            thread_close_error = cls._windows_close_startup_handle(
                int(thread_handle)
            )
        if prior_suspend_count == wintypes.DWORD(-1).value:
            detail = (
                f"; {thread_close_error}"
                if thread_close_error is not None
                else ""
            )
            return f"ResumeThread failed: {resume_error}{detail}"
        return thread_close_error


__all__: list[str] = ["FlextCliUtilitiesRuntimeWindowsProcessResumeMixin"]
