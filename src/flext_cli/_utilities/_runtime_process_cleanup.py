"""Signal forwarding and deterministic streamed-process cleanup.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import signal
import threading
import time
from collections.abc import Callable
from functools import partial
from types import FrameType

from flext_cli import m, p, r, t
from flext_cli._utilities import (
    FlextCliUtilitiesRuntimeProcessMonitorMixin,
    FlextCliUtilitiesRuntimeProcessThreadsMixin,
)


class FlextCliUtilitiesRuntimeProcessCleanupMixin(
    FlextCliUtilitiesRuntimeProcessMonitorMixin,
    FlextCliUtilitiesRuntimeProcessThreadsMixin,
):
    """Forward signals, kill descendants, reap root, and drain output."""

    @classmethod
    def _install_forwarding_handlers(
        cls,
        received_signals: t.MutableSequenceOf[int],
        forwarded_signals: t.MutableSequenceOf[int],
        wake: threading.Event,
    ) -> t.MutableSequenceOf[Callable[[], None]]:
        """Capture operator signals before opening the containment window.

        Returns:
            The callbacks that restore the original parent signal handlers.

        Raises:
            OSError: If a ``(OSError, ValueError)`` is caught.
            ValueError: If a ``(OSError, ValueError)`` is caught.

        """
        restore_handlers: t.MutableSequenceOf[Callable[[], None]] = []

        def forward(signal_number: int, _frame: FrameType | None) -> None:
            received_signals.append(signal_number)
            wake.set()

        forwarded = (signal.SIGINT, signal.SIGTERM)
        if os.name != "nt" and hasattr(signal, "SIGHUP"):
            forwarded = (*forwarded, signal.SIGHUP)
        try:
            for signal_number in forwarded:
                previous: t.Cli.SignalHandler = signal.getsignal(signal_number)
                signal.signal(signal_number, forward)
                forwarded_signals.append(int(signal_number))
                restore_handlers.append(
                    partial(cls._restore_signal_handler, int(signal_number), previous),
                )
        except (OSError, ValueError):
            for restore in reversed(restore_handlers):
                restore()
            raise
        return restore_handlers

    @staticmethod
    def _restore_signal_handler(
        signal_number: int,
        handler: t.Cli.SignalHandler,
    ) -> None:
        """Restore the captured handler without exposing the displaced handler."""
        signal.signal(signal_number, handler)

    @staticmethod
    def _restore_forwarding_handlers(
        restore_handlers: t.SequenceOf[Callable[[], None]],
    ) -> t.VariadicTuple[str]:
        """Restore parent handlers after child lifecycle completion.

        Returns:
            The resulting ``t.VariadicTuple[str]``.

        """
        failures: t.MutableSequenceOf[str] = []
        for restore in reversed(restore_handlers):
            try:
                restore()
            except (OSError, ValueError) as exc:
                # Why: cleanup continues across every handler; each failure is
                # propagated as typed causal evidence via r.fail(...).error
                # (silent-failure-broad-except), never silently dropped.
                failures.append(
                    r[str]
                    .fail(f"signal handler restore failed: {exc}", exception=exc)
                    .error
                    or str(exc),
                )
        return tuple(failures)

    @classmethod
    def _reap_and_drain(
        cls,
        process: p.Cli.ProcessHandle,
        waiter: threading.Thread,
        state: m.Cli.RuntimeProcessState,
    ) -> int | None:
        """Kill the owned boundary, reap root, drain output, and prove empty.

        Returns:
            The resulting ``int | None``.

        """
        cleanup_deadline = (
            state.final_deadline
            if state.final_deadline is not None
            else time.monotonic() + 1.0
        )
        cls._empty_owned_boundary(
            process,
            state,
            cleanup_deadline,
        )
        waiter.join(cls._remaining(cleanup_deadline))
        if waiter.is_alive():
            state.cleanup_errors.append("process deadline expired before root reaping")
        if state.input_pump is not None:
            cls._drain_input(
                state.input_pump[0],
                state.input_pump[1],
                state.cleanup_errors,
                cleanup_deadline,
            )
        for pump, source in tuple(state.pump_streams):
            cls._drain_output(
                pump,
                state.pump_stop,
                source,
                state.cleanup_errors,
                cleanup_deadline,
            )
        return state.return_codes[0] if state.return_codes else process.poll()

    @classmethod
    def _drain_input(
        cls,
        pump: threading.Thread,
        sink: p.Cli.RuntimeClosableStream,
        cleanup_errors: t.MutableSequenceOf[str],
        cleanup_deadline: float,
    ) -> None:
        """Join the input writer after the child boundary has lost every reader."""
        pump.join(cls._remaining(cleanup_deadline))
        if pump.is_alive():
            try:
                sink.close()
            except (OSError, ValueError) as exc:
                cleanup_errors.append(
                    r[str]
                    .fail(f"process input close error: {exc}", exception=exc)
                    .error
                    or str(exc),
                )
            pump.join(cls._remaining(cleanup_deadline))
        if pump.is_alive():
            cleanup_errors.append("process deadline expired before input drain")

    @classmethod
    def _empty_owned_boundary(
        cls,
        process: p.Cli.ProcessHandle,
        state: m.Cli.RuntimeProcessState,
        cleanup_deadline: float,
    ) -> None:
        boundary = cls._process_boundary_empty(process.pid, state.job_handle)
        if boundary.success and boundary.value:
            return
        cls._append_signal_error(
            state.cleanup_errors,
            cls._signal_process_tree(
                process,
                signal.SIGTERM,
                state.job_handle,
                force=False,
            ),
        )
        state.process_done.wait(min(0.1, cls._remaining(cleanup_deadline)))
        boundary = cls._process_boundary_empty(process.pid, state.job_handle)
        if boundary.success and not boundary.value:
            cls._append_signal_error(
                state.cleanup_errors,
                cls._signal_process_tree(
                    process,
                    signal.SIGKILL,
                    state.job_handle,
                    force=True,
                ),
            )
        while (
            boundary.success
            and not boundary.value
            and cls._remaining(cleanup_deadline) > 0
        ):
            state.wake.wait(min(0.02, cls._remaining(cleanup_deadline)))
            state.wake.clear()
            boundary = cls._process_boundary_empty(process.pid, state.job_handle)
        if boundary.failure:
            state.cleanup_errors.append(
                boundary.error or "owned process-boundary probe failed",
            )
        elif not boundary.value:
            state.cleanup_errors.append(
                "owned process boundary was not empty before return",
            )

    @classmethod
    def _drain_output(
        cls,
        pump: threading.Thread,
        stop: threading.Event,
        source: p.Cli.RuntimeClosableStream,
        cleanup_errors: t.MutableSequenceOf[str],
        cleanup_deadline: float,
    ) -> None:
        pump.join(cls._remaining(cleanup_deadline))
        if pump.is_alive():
            stop.set()
            try:
                source.close()
            except (OSError, ValueError) as exc:
                cleanup_errors.append(
                    r[str]
                    .fail(f"process output close error: {exc}", exception=exc)
                    .error
                    or str(exc),
                )
            pump.join(cls._remaining(cleanup_deadline))
        if pump.is_alive():
            cleanup_errors.append("process deadline expired before output drain")

    @staticmethod
    def _append_signal_error(
        errors: t.MutableSequenceOf[str],
        signal_result: p.Result[bool],
    ) -> None:
        if signal_result.failure:
            errors.append(signal_result.error or "process signal failed")

    @staticmethod
    def _remaining(absolute_deadline: float) -> float:
        return max(0.0, absolute_deadline - time.monotonic())


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessCleanupMixin"]
