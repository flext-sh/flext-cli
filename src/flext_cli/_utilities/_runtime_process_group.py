"""Portable process-group lifecycle primitives for ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import platform
import signal

from flext_cli import p, r

from ._runtime_darwin_process_group import (
    FlextCliUtilitiesRuntimeDarwinProcessGroupMixin,
)
from ._runtime_windows_job_start import FlextCliUtilitiesRuntimeWindowsJobStartMixin
from ._runtime_windows_job_state import FlextCliUtilitiesRuntimeWindowsJobStateMixin


class FlextCliUtilitiesRuntimeProcessGroupMixin(
    FlextCliUtilitiesRuntimeDarwinProcessGroupMixin,
    FlextCliUtilitiesRuntimeWindowsJobStartMixin,
    FlextCliUtilitiesRuntimeWindowsJobStateMixin,
):
    """Own POSIX process groups and Windows kill-on-close Job Objects."""

    @classmethod
    def _process_boundary_empty(
        cls,
        process_group_id: int,
        job_handle: int,
    ) -> p.Result[bool]:
        """Prove the owned group/Job has no active members.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        if os.name == "nt":
            return cls.windows_job_active_count(job_handle).map(
                lambda active_count: active_count == 0,
            )
        try:
            if platform.system() == "Darwin":
                return r[bool].ok(
                    not cls._darwin_process_group_members(process_group_id),
                )
            os.killpg(process_group_id, 0)
        except ProcessLookupError:
            return r[bool].ok(True)
        except OSError as exc:
            return r[bool].fail(f"process-group probe failed: {exc}", exception=exc)
        return r[bool].ok(False)

    @classmethod
    def _signal_process_tree_windows(
        cls,
        process: p.Cli.ProcessHandle,
        signal_number: int,
        job_handle: int,
        *,
        force: bool,
    ) -> p.Result[bool]:
        """Signal one owned process tree through the Windows Job Object.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        if not force and signal_number == signal.SIGINT:
            process.send_signal(int(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGINT)))
            return r[bool].ok(True)
        terminate_error = cls._windows_job_terminate(
            job_handle,
            128 + abs(signal_number),
        )
        if terminate_error is not None:
            return r[bool].fail(terminate_error)
        return r[bool].ok(True)

    @classmethod
    def _signal_process_tree(
        cls,
        process: p.Cli.ProcessHandle,
        signal_number: int,
        job_handle: int,
        *,
        force: bool,
    ) -> p.Result[bool]:
        """Signal the complete owned process tree.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        if os.name == "nt":
            return cls._signal_process_tree_windows(
                process,
                signal_number,
                job_handle,
                force=force,
            )
        try:
            os.killpg(process.pid, signal.SIGKILL if force else signal_number)
        except ProcessLookupError:
            return r[bool].ok(True)
        except PermissionError as exc:
            # XNU killpg excludes zombies and returns EPERM if none are live.
            # Confirm that state; cleanup still waits for every PID to be reaped.
            if platform.system() == "Darwin":
                try:
                    if cls._darwin_process_group_exited(process.pid):
                        return r[bool].ok(True)
                except OSError as probe_error:
                    return r[bool].fail(
                        f"process-tree state error: {probe_error}",
                        exception=probe_error,
                    )
            return r[bool].fail(f"process-tree signal error: {exc}", exception=exc)
        except (OSError, ValueError) as exc:
            return r[bool].fail(f"process-tree signal error: {exc}", exception=exc)
        return r[bool].ok(True)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessGroupMixin"]
