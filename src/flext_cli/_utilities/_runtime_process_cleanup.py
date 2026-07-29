"""Signal forwarding and deterministic streamed-process cleanup."""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable
from types import FrameType
from typing import BinaryIO

from flext_cli._utilities._runtime_process_monitor import (
    FlextCliUtilitiesRuntimeProcessMonitorMixin,
)
from flext_cli._utilities._runtime_process_stream import (
    FlextCliUtilitiesRuntimeProcessStreamMixin,
)


class FlextCliUtilitiesRuntimeProcessCleanupMixin(
    FlextCliUtilitiesRuntimeProcessMonitorMixin,
    FlextCliUtilitiesRuntimeProcessStreamMixin,
):
    """Forward signals, kill descendants, reap root, and drain output."""

    @classmethod
    def _install_forwarding_handlers(
        cls,
        received_signals: list[int],
    ) -> list[
        tuple[
            signal.Signals,
            signal.Handlers | Callable[[int, FrameType | None], object],
        ]
    ]:
        """Capture operator signals before opening the containment window."""
        previous_handlers: list[
            tuple[
                signal.Signals,
                signal.Handlers | Callable[[int, FrameType | None], object],
            ]
        ] = []

        def forward(signal_number: int, _frame: FrameType | None) -> None:
            received_signals.append(signal_number)

        forwarded = (signal.SIGINT, signal.SIGTERM)
        if os.name != "nt" and hasattr(signal, "SIGHUP"):
            forwarded = (*forwarded, signal.SIGHUP)
        for signal_number in forwarded:
            previous = signal.getsignal(signal_number)
            signal.signal(signal_number, forward)
            previous_handlers.append((signal_number, previous))
        return previous_handlers

    @staticmethod
    def _restore_forwarding_handlers(
        previous_handlers: list[
            tuple[
                signal.Signals,
                signal.Handlers | Callable[[int, FrameType | None], object],
            ]
        ],
    ) -> None:
        """Restore parent handlers after child lifecycle completion."""
        for signal_number, previous in reversed(previous_handlers):
            signal.signal(signal_number, previous)

    @classmethod
    def _reap_and_drain(
        cls,
        process: subprocess.Popen[bytes],
        pump: threading.Thread,
        stop: threading.Event,
        source: BinaryIO,
        cleanup_errors: list[str],
        job_handle: int,
        drain_at: float | None,
        flush_at: float | None,
    ) -> int | None:
        """Kill the owned boundary, reap root, drain output, and prove empty."""
        error = cls._signal_process_tree(
            process, signal.SIGKILL, job_handle, force=True
        )
        if error is not None:
            cleanup_errors.append(error)
        wait_seconds = (
            max(0.0, drain_at - time.monotonic())
            if drain_at is not None
            else cls._SIGNAL_CLEANUP_SECONDS
        )
        try:
            return_code = process.wait(timeout=wait_seconds)
        except subprocess.TimeoutExpired:
            cleanup_errors.append("process deadline expired before root reaping")
            return_code = process.poll()
        cleanup_deadline = (
            flush_at
            if flush_at is not None
            else time.monotonic() + cls._SIGNAL_CLEANUP_SECONDS
        )
        boundary = cls._process_boundary_empty(process.pid, job_handle)
        while (
            boundary.success
            and not boundary.value
            and time.monotonic() < cleanup_deadline
        ):
            time.sleep(cls._PROCESS_POLL_SECONDS)
            boundary = cls._process_boundary_empty(process.pid, job_handle)
        if boundary.failure:
            cleanup_errors.append(
                boundary.error or "owned process-boundary probe failed"
            )
        elif not boundary.value:
            cleanup_errors.append("owned process boundary was not empty before return")
        pump.join(
            max(0.0, cleanup_deadline - time.monotonic())
        )
        if pump.is_alive():
            stop.set()
            try:
                source.close()
            except (OSError, ValueError) as exc:
                cleanup_errors.append(f"combined output close error: {exc}")
            pump.join(max(0.0, cleanup_deadline - time.monotonic()))
        if pump.is_alive():
            cleanup_errors.append("process deadline expired before output drain")
        return return_code


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessCleanupMixin"]
