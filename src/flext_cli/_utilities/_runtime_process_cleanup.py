"""Signal forwarding and deterministic streamed-process cleanup."""

from __future__ import annotations

import signal
import subprocess
import threading
import time
from typing import BinaryIO

from flext_cli import p
from flext_cli._utilities._runtime_process_monitor import (
    FlextCliUtilitiesRuntimeProcessMonitorMixin,
)
from flext_cli._utilities._runtime_process_signals import (
    FlextCliUtilitiesRuntimeProcessSignalsMixin,
)
from flext_cli._utilities._runtime_process_stream import (
    FlextCliUtilitiesRuntimeProcessStreamMixin,
)


class FlextCliUtilitiesRuntimeProcessCleanupMixin(
    FlextCliUtilitiesRuntimeProcessMonitorMixin,
    FlextCliUtilitiesRuntimeProcessSignalsMixin,
    FlextCliUtilitiesRuntimeProcessStreamMixin,
):
    """Forward signals, kill descendants, reap root, and drain output."""

    @classmethod
    def _reap_and_drain(
        cls,
        process: p.Cli.ProcessHandle,
        pump: threading.Thread | None,
        stop: threading.Event,
        source: BinaryIO | None,
        cleanup_errors: list[str],
        job_handle: int,
        drain_at: float | None,
        flush_at: float | None,
        final_deadline: float | None,
    ) -> int | None:
        """Kill the owned boundary, reap root, drain output, and prove empty."""
        cleanup_deadline = (
            final_deadline
            if final_deadline is not None
            else time.monotonic() + cls._SIGNAL_CLEANUP_SECONDS
        )
        error = cls._signal_process_tree(
            process, signal.SIGKILL, job_handle, force=True
        )
        if error is not None:
            cleanup_errors.append(error)
        wait_seconds = (
            max(
                0.0,
                min(drain_at, cleanup_deadline) - time.monotonic(),
            )
            if drain_at is not None
            else max(0.0, cleanup_deadline - time.monotonic())
        )
        try:
            return_code = process.wait(timeout=wait_seconds)
        except subprocess.TimeoutExpired:
            cleanup_errors.append("process deadline expired before root reaping")
            return_code = process.poll()
        boundary_deadline = (
            min(flush_at, cleanup_deadline)
            if flush_at is not None
            else cleanup_deadline
        )
        boundary = cls._process_boundary_empty(process.pid, job_handle)
        while (
            boundary.success
            and not boundary.value
            and time.monotonic() < boundary_deadline
        ):
            error = cls._signal_process_tree(
                process, signal.SIGKILL, job_handle, force=True
            )
            if error is not None:
                cleanup_errors.append(error)
            time.sleep(
                min(
                    cls._PROCESS_POLL_SECONDS,
                    max(0.0, boundary_deadline - time.monotonic()),
                )
            )
            boundary = cls._process_boundary_empty(process.pid, job_handle)
        if boundary.failure:
            cleanup_errors.append(
                boundary.error or "owned process-boundary probe failed"
            )
        if pump is not None:
            pump.join(max(0.0, boundary_deadline - time.monotonic()))
            if pump.is_alive():
                stop.set()
                if source is not None:
                    try:
                        source.close()
                    except (OSError, ValueError) as exc:
                        cleanup_errors.append(
                            f"combined output close error: {exc}"
                        )
                pump.join(max(0.0, cleanup_deadline - time.monotonic()))
            if pump.is_alive():
                cleanup_errors.append(
                    "process deadline expired before output pump stopped"
                )
        if process.poll() is None:
            try:
                return_code = process.wait(
                    timeout=max(0.0, cleanup_deadline - time.monotonic())
                )
            except subprocess.TimeoutExpired:
                cleanup_errors.append(
                    "process deadline expired before final root reap"
                )
        boundary = cls._process_boundary_empty(process.pid, job_handle)
        while (
            boundary.success
            and not boundary.value
            and time.monotonic() < cleanup_deadline
        ):
            error = cls._signal_process_tree(
                process, signal.SIGKILL, job_handle, force=True
            )
            if error is not None:
                cleanup_errors.append(error)
            time.sleep(
                min(
                    cls._PROCESS_POLL_SECONDS,
                    max(0.0, cleanup_deadline - time.monotonic()),
                )
            )
            boundary = cls._process_boundary_empty(process.pid, job_handle)
        if boundary.failure:
            cleanup_errors.append(
                boundary.error or "final process-boundary probe failed"
            )
        elif not boundary.value:
            cleanup_errors.append(
                "owned process boundary was not empty before return"
            )
        return return_code


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessCleanupMixin"]
