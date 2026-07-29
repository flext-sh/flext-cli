"""Absolute-deadline monitoring for streamed process execution."""

from __future__ import annotations

import signal
import subprocess
import threading
import time
from typing import ClassVar

from flext_cli._utilities._runtime_process_group import (
    FlextCliUtilitiesRuntimeProcessGroupMixin,
)


class FlextCliUtilitiesRuntimeProcessMonitorMixin(
    FlextCliUtilitiesRuntimeProcessGroupMixin
):
    """Monitor one process group and reserve bounded cleanup time."""

    _PROCESS_POLL_SECONDS: ClassVar[float] = 0.02
    _SIGNAL_CLEANUP_SECONDS: ClassVar[float] = 1.0

    @classmethod
    def _monitor_process(
        cls,
        process: subprocess.Popen[bytes],
        pump: threading.Thread,
        failures: list[str],
        received_signals: list[int],
        job_handle: int,
        absolute_deadline: float | None,
        grace_seconds: float,
    ) -> tuple[bool, float | None, float | None, float | None]:
        """Monitor until root exit or the reserved reap boundary."""
        soft_at = (
            absolute_deadline - grace_seconds
            if absolute_deadline is not None
            else None
        )
        hard_at = (
            soft_at + (grace_seconds / 2.0) if soft_at is not None else None
        )
        reap_at = (
            absolute_deadline - (grace_seconds / 4.0)
            if absolute_deadline is not None
            else None
        )
        drain_at = (
            absolute_deadline - (grace_seconds / 8.0)
            if absolute_deadline is not None
            else None
        )
        flush_at = (
            absolute_deadline - (grace_seconds / 16.0)
            if absolute_deadline is not None
            else None
        )
        interrupt_deadline: float | None = None
        timed_out = False
        forced = False
        forwarded_count = 0
        while process.poll() is None:
            now = time.monotonic()
            if failures and not forced:
                error = cls._signal_process_tree(
                    process, signal.SIGKILL, job_handle, force=True
                )
                if error is not None:
                    failures.append(error)
                forced = True
            if received_signals and interrupt_deadline is None:
                interrupt_deadline = min(
                    absolute_deadline
                    if absolute_deadline is not None
                    else now + cls._SIGNAL_CLEANUP_SECONDS,
                    now + cls._SIGNAL_CLEANUP_SECONDS,
                )
                reserve = max(0.0, interrupt_deadline - now)
                hard_at = now + (reserve / 2.0)
                reap_at = now + ((reserve * 3.0) / 4.0)
                drain_at = now + ((reserve * 7.0) / 8.0)
                flush_at = now + ((reserve * 15.0) / 16.0)
            while forwarded_count < len(received_signals):
                error = cls._signal_process_tree(
                    process,
                    received_signals[forwarded_count],
                    job_handle,
                    force=forwarded_count > 0,
                )
                if error is not None:
                    failures.append(error)
                forwarded_count += 1
                forced = forced or forwarded_count > 1
            if (
                soft_at is not None
                and now >= soft_at
                and not timed_out
                and not received_signals
            ):
                timed_out = True
                error = cls._signal_process_tree(
                    process, signal.SIGINT, job_handle, force=False
                )
                if error is not None:
                    failures.append(error)
            if hard_at is not None and now >= hard_at and not forced:
                error = cls._signal_process_tree(
                    process, signal.SIGKILL, job_handle, force=True
                )
                if error is not None:
                    failures.append(error)
                forced = True
            if reap_at is not None and now >= reap_at:
                break
            wait_seconds = cls._PROCESS_POLL_SECONDS
            if reap_at is not None:
                wait_seconds = min(wait_seconds, max(0.0, reap_at - now))
            pump.join(wait_seconds)
        final_deadline = (
            interrupt_deadline
            if interrupt_deadline is not None
            else absolute_deadline
        )
        return timed_out, final_deadline, drain_at, flush_at


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessMonitorMixin"]
