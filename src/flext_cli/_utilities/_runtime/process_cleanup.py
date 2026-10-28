"""Signal forwarding and deterministic streamed-process cleanup.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import signal
import threading
import time
from collections.abc import Callable, Generator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, nullcontext
from contextvars import copy_context
from functools import partial
from types import FrameType

from flext_cli import m, p, r, t
from flext_cli._utilities._runtime import (
    FlextCliUtilitiesRuntimeProcessMonitor,
    FlextCliUtilitiesRuntimeProcessThreads,
)


class FlextCliUtilitiesRuntimeProcessCleanup(
    FlextCliUtilitiesRuntimeProcessMonitor,
    FlextCliUtilitiesRuntimeProcessThreads,
):
    """Forward signals, kill descendants, reap root, and drain output."""

    class SignalWave:
        """One wave of worker-thread lifecycles sharing main-thread signal forwarding.

        The owner installs the operator-signal handlers on the main thread
        and broadcasts each received signal; every worker lifecycle started
        with this wave subscribes its own signal record and wake event, and
        its monitor forwards the signal to the process group it owns.
        """

        def __init__(self) -> None:
            """Start the wave with no subscribed lifecycle."""
            self._lock = threading.Lock()
            self._subscribers: t.MutableMappingKV[
                int, t.Pair[t.MutableSequenceOf[int], threading.Event]
            ] = {}

        def subscribe(
            self,
            received_signals: t.MutableSequenceOf[int],
            wake: threading.Event,
        ) -> Callable[[], None]:
            """Deliver each received signal to one lifecycle until unsubscribed.

            Returns:
                The callback that removes the subscription at lifecycle cleanup.

            """
            key = id(received_signals)
            with self._lock:
                self._subscribers[key] = (received_signals, wake)
            return partial(self._unsubscribe, key)

        def broadcast(self, signal_number: int) -> None:
            """Deliver one operator signal to every subscribed lifecycle."""
            with self._lock:
                subscribers = tuple(self._subscribers.values())
            for received_signals, wake in subscribers:
                received_signals.append(signal_number)
                wake.set()

        def _unsubscribe(self, key: int) -> None:
            """Remove one lifecycle from the wave."""
            with self._lock:
                self._subscribers.pop(key, None)

    @classmethod
    @contextmanager
    def process_signal_wave(cls) -> Generator[p.Cli.SignalWave]:
        """Own operator-signal forwarding for lifecycles run in worker threads.

        Signal handlers install only on the main interpreter thread, so the
        main thread installs them once and yields the wave every worker
        lifecycle receives explicitly. Timeout and cleanup semantics stay per
        lifecycle.

        Yields:
            The wave to pass to the worker-thread lifecycles.

        Raises:
            RuntimeError: If entered off the main interpreter thread.

        """
        if threading.current_thread() is not threading.main_thread():
            msg = "a process signal wave must be owned by the main interpreter thread"
            raise RuntimeError(msg)
        wave = cls.SignalWave()
        received: t.MutableSequenceOf[int] = []
        forwarded: t.MutableSequenceOf[int] = []
        restore_handlers = cls._install_forwarding_handlers(
            received,
            forwarded,
            threading.Event(),
            on_signal=wave.broadcast,
        )
        try:
            yield wave
        finally:
            failures = cls._restore_forwarding_handlers(restore_handlers)
            if failures:
                msg = "; ".join(failures)
                raise RuntimeError(msg)

    @classmethod
    def run_in_signal_wave[T](
        cls,
        tasks: t.SequenceOf[Callable[[p.Cli.SignalWave], T]],
        *,
        max_workers: int,
        signal_wave: p.Cli.SignalWave | None = None,
    ) -> t.VariadicTuple[T]:
        """Run independent tasks concurrently, each receiving its signal wave.

        Without ``signal_wave`` the call owns a new wave on the main thread;
        a task of an outer wave passes that wave to run nested tasks in it.
        Each task runs with a copy of the caller's context. The first task
        exception escapes in task order.

        Returns:
            Every task's result, in task order.

        """
        with (
            (
                cls.process_signal_wave()
                if signal_wave is None
                else nullcontext(signal_wave)
            ) as wave,
            ThreadPoolExecutor(max_workers=max_workers) as pool,
        ):
            futures = tuple(
                pool.submit(copy_context().run, task, wave) for task in tasks
            )
            return tuple(future.result() for future in futures)

    @classmethod
    def _install_forwarding_handlers(
        cls,
        received_signals: t.MutableSequenceOf[int],
        forwarded_signals: t.MutableSequenceOf[int],
        wake: threading.Event,
        *,
        on_signal: Callable[[int], None] | None = None,
    ) -> t.MutableSequenceOf[Callable[[], None]]:
        """Capture operator signals before opening the containment window.

        ``on_signal`` additionally delivers each signal to the subscribers of
        a signal wave.

        Returns:
            The callbacks that restore the original parent signal handlers.

        Raises:
            OSError: If a ``(OSError, ValueError)`` is caught.
            ValueError: If a ``(OSError, ValueError)`` is caught.

        """
        restore_handlers: t.MutableSequenceOf[Callable[[], None]] = []

        def forward(
            previous: t.Cli.SignalHandler | p.Cli.ParentSignalObserver,
            signal_number: int,
            frame: FrameType | None,
        ) -> None:
            received_signals.append(signal_number)
            wake.set()
            if on_signal is not None:
                on_signal(signal_number)
            if isinstance(previous, p.Cli.ParentSignalObserver):
                previous.on_operator_signal(signal_number, frame)

        forwarded = (signal.SIGINT, signal.SIGTERM)
        if os.name != "nt" and hasattr(signal, "SIGHUP"):
            forwarded = (*forwarded, signal.SIGHUP)
        try:
            for signal_number in forwarded:
                previous: t.Cli.SignalHandler = signal.getsignal(signal_number)
                signal.signal(signal_number, partial(forward, previous))
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
            cls._drain_stream(
                state.input_pump[0],
                state.input_pump[1],
                state,
                cleanup_deadline,
                direction="input",
            )
        for pump, source in tuple(state.pump_streams):
            cls._drain_stream(
                pump,
                source,
                state,
                cleanup_deadline,
                direction="output",
            )
        return state.return_codes[0] if state.return_codes else process.poll()

    @classmethod
    def _drain_stream(
        cls,
        pump: threading.Thread,
        stream: p.Cli.RuntimeClosableStream,
        state: m.Cli.RuntimeProcessState,
        cleanup_deadline: float,
        *,
        direction: str,
    ) -> None:
        """Join a pipe pump, close a blocked stream, and preserve causal errors."""
        pump.join(cls._remaining(cleanup_deadline))
        if pump.is_alive():
            if direction == "output":
                state.pump_stop.set()
            try:
                stream.close()
            except (OSError, ValueError) as exc:
                state.cleanup_errors.append(
                    r[str]
                    .fail(f"process {direction} close error: {exc}", exception=exc)
                    .error
                    or str(exc),
                )
            pump.join(cls._remaining(cleanup_deadline))
        if pump.is_alive():
            state.cleanup_errors.append(
                f"process deadline expired before {direction} drain",
            )

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


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessCleanup"]
