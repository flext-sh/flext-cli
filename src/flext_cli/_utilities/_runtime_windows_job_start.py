"""Windows Job Object creation and suspended-process startup."""

from __future__ import annotations

import os

from flext_cli import p, r


class FlextCliUtilitiesRuntimeWindowsJobStartMixin:
    """Contain a suspended Windows process before any child code executes."""

    @staticmethod
    def _windows_close_startup_handle(handle: int) -> str | None:
        """Close one temporary Windows startup handle and report any leak."""
        if os.name != "nt" or handle == 0:
            return None
        try:
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            close_handle = kernel32.CloseHandle
            close_handle.argtypes = (wintypes.HANDLE,)
            close_handle.restype = wintypes.BOOL
            if not close_handle(handle):
                return f"CloseHandle failed: {ctypes.get_last_error()}"
        except (OSError, TypeError, ValueError) as exc:
            return f"Windows startup handle close error: {exc}"
        return None

    @classmethod
    def _windows_job_create(
        cls, process: p.Cli.ProcessHandle
    ) -> p.Result[int]:
        """Assign a suspended Windows process to a kill-on-close Job Object."""
        if os.name != "nt":
            return r[int].ok(0)
        job_handle = 0
        process_handle = 0
        try:
            import ctypes
            from ctypes import wintypes

            class _IoCounters(ctypes.Structure):
                _fields_ = [
                    ("ReadOperationCount", ctypes.c_uint64),
                    ("WriteOperationCount", ctypes.c_uint64),
                    ("OtherOperationCount", ctypes.c_uint64),
                    ("ReadTransferCount", ctypes.c_uint64),
                    ("WriteTransferCount", ctypes.c_uint64),
                    ("OtherTransferCount", ctypes.c_uint64),
                ]

            class _BasicLimitInformation(ctypes.Structure):
                _fields_ = [
                    ("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD),
                ]

            class _ExtendedLimitInformation(ctypes.Structure):
                _fields_ = [
                    ("BasicLimitInformation", _BasicLimitInformation),
                    ("IoInfo", _IoCounters),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t),
                ]

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            create_job = kernel32.CreateJobObjectW
            create_job.argtypes = (wintypes.LPVOID, wintypes.LPCWSTR)
            create_job.restype = wintypes.HANDLE
            set_job = kernel32.SetInformationJobObject
            set_job.argtypes = (
                wintypes.HANDLE,
                ctypes.c_int,
                wintypes.LPVOID,
                wintypes.DWORD,
            )
            set_job.restype = wintypes.BOOL
            open_process = kernel32.OpenProcess
            open_process.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
            open_process.restype = wintypes.HANDLE
            assign_process = kernel32.AssignProcessToJobObject
            assign_process.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
            assign_process.restype = wintypes.BOOL
            job_handle = create_job(None, None)
            if not job_handle:
                return r[int].fail(
                    f"CreateJobObjectW failed: {ctypes.get_last_error()}"
                )
            info = _ExtendedLimitInformation()
            info.BasicLimitInformation.LimitFlags = 0x00002000
            if not set_job(job_handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                error = ctypes.get_last_error()
                close_error = cls._windows_close_startup_handle(job_handle)
                job_handle = 0
                detail = f"; {close_error}" if close_error is not None else ""
                return r[int].fail(
                    f"SetInformationJobObject failed: {error}{detail}"
                )
            process_handle = open_process(0x0001 | 0x0100, False, process.pid)
            if not process_handle:
                error = ctypes.get_last_error()
                close_error = cls._windows_close_startup_handle(job_handle)
                job_handle = 0
                detail = f"; {close_error}" if close_error is not None else ""
                return r[int].fail(f"OpenProcess failed: {error}{detail}")
            assigned = assign_process(job_handle, process_handle)
            assignment_error = ctypes.get_last_error() if not assigned else 0
            process_close_error = cls._windows_close_startup_handle(process_handle)
            process_handle = 0
            if not assigned or process_close_error is not None:
                job_close_error = cls._windows_close_startup_handle(job_handle)
                job_handle = 0
                diagnostics = tuple(
                    detail
                    for detail in (process_close_error, job_close_error)
                    if detail is not None
                )
                detail = f"; {'; '.join(diagnostics)}" if diagnostics else ""
                failure = (
                    f"AssignProcessToJobObject failed: {assignment_error}"
                    if not assigned
                    else "Windows process handle cleanup failed"
                )
                return r[int].fail(
                    f"{failure}{detail}"
                )
            return r[int].ok(int(job_handle))
        except (OSError, TypeError, ValueError) as exc:
            cleanup_errors = [
                error
                for error in (
                    cls._windows_close_startup_handle(process_handle),
                    cls._windows_close_startup_handle(job_handle),
                )
                if error is not None
            ]
            detail = (
                f"; {'; '.join(cleanup_errors)}" if cleanup_errors else ""
            )
            return r[int].fail(f"Windows Job Object error: {exc}{detail}")

__all__: list[str] = ["FlextCliUtilitiesRuntimeWindowsJobStartMixin"]
