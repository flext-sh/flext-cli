"""Resource ownership for one portable streamed process lifecycle."""

from __future__ import annotations

import contextlib
import os
import signal
import threading
import time
from collections.abc import Callable
from pathlib import Path
from types import FrameType
from typing import BinaryIO

from flext_cli import c, p, t
from flext_cli._utilities._runtime_process_cleanup import (
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
)
from flext_cli._utilities._runtime_process_outcome import (
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
)
from flext_cli._utilities._runtime_process_resources import (
    FlextCliUtilitiesRuntimeProcessResourcesMixin,
)
from flext_cli._utilities._runtime_process_start import (
    FlextCliUtilitiesRuntimeProcessStartMixin,
)


class FlextCliUtilitiesRuntimeProcessExecutionMixin(
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
    FlextCliUtilitiesRuntimeProcessResourcesMixin,
    FlextCliUtilitiesRuntimeProcessStartMixin,
):
    """Own one child process and its streaming resources."""

    @classmethod
    def _execute_streamed_process(
        cls,
        cmd: t.StrSequence,
        output_path: Path,
        cwd: t.Cli.TextPath | None,
        env: dict[str, str] | None,
        input_data: str | bytes | None,
        *,
        live: bool,
        absolute_deadline: float | None,
        grace_seconds: float,
        timeout_exit_code: int,
        legacy_timeout: bool,
        legacy_timeout_seconds: int | None,
    ) -> p.Result[int]:
        """Own resources and complete one streamed child lifecycle."""
        process: p.Cli.ProcessHandle | None = None
        waiter: threading.Thread | None = None
        pump: threading.Thread | None = None
        source: BinaryIO | None = None
        durable_log: BinaryIO | None = None
        job_handle = 0
        failures: list[str] = []
        cleanup_errors: list[str] = []
        live_diagnostics: list[str] = []
        previous_handlers: list[
            tuple[
                signal.Signals,
                signal.Handlers | Callable[[int, FrameType | None], object],
            ]
        ] = []
        previous_signal_mask: set[signal.Signals] | None = None
        received_signals: list[int] = []
        return_codes: list[int] = []
        pump_stop = threading.Event()
        process_done = threading.Event()
        wake = threading.Event()
        stack = contextlib.ExitStack()
        return_code: int | None = None
        timed_out = False
        final_deadline = absolute_deadline
        cleanup_complete = False
        try:
            if threading.current_thread() is threading.main_thread():
                previous_handlers = cls._install_forwarding_handlers(
                    received_signals, wake
                )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            durable_log = stack.enter_context(output_path.open("wb", buffering=0))
            stdin_result = cls._prepare_streamed_stdin(stack, input_data)
            live_result = cls._prepare_live_descriptor(stack, live=live)
            if stdin_result.failure:
                failures.append(stdin_result.error or "stdin preparation failed")
            elif live_result.failure:
                failures.append(live_result.error or "live output preparation failed")
            elif received_signals:
                wake.set()
            elif cls._spawn_deadline_exhausted(absolute_deadline, grace_seconds):
                failures.append("process deadline exhausted before child spawn")
            else:
                previous_signal_mask = cls._block_forwarded_signals(
                    previous_handlers
                )
                started = cls._start_contained_process(
                    cmd, cwd, env, stdin_result.value
                )
                if started.failure:
                    failures.append(started.error or "process start failed")
                else:
                    process, job_handle = started.value
                    previous_signal_mask = cls._restore_signal_mask(
                        previous_signal_mask
                    )
                    source = process.stdout
                    if source is None:
                        failures.append("combined output pipe unavailable")
                    else:
                        stack.callback(source.close)
                        waiter = cls._start_root_waiter(
                            process,
                            return_codes,
                            failures,
                            process_done,
                            wake,
                        )
                        pump = cls._start_output_pump(
                            source,
                            durable_log,
                            live_result.value,
                            failures,
                            live_diagnostics,
                            pump_stop,
                            wake,
                        )
                        timed_out, final_deadline = cls._monitor_process(
                            process,
                            process_done,
                            wake,
                            failures,
                            received_signals,
                            job_handle,
                            absolute_deadline,
                            grace_seconds,
                        )
                        return_code = cls._reap_and_drain(
                            process,
                            waiter,
                            pump,
                            process_done,
                            wake,
                            pump_stop,
                            source,
                            cleanup_errors,
                            job_handle,
                            final_deadline,
                            return_codes,
                        )
                        cleanup_complete = True
        except c.EXC_OS_VALUE as exc:
            failures.append(f"execution error: {exc}")
        finally:
            previous_signal_mask = cls._restore_signal_mask(previous_signal_mask)
            if (
                process is not None
                and waiter is not None
                and pump is not None
                and source is not None
                and not cleanup_complete
            ):
                return_code = cls._reap_and_drain(
                    process,
                    waiter,
                    pump,
                    process_done,
                    wake,
                    pump_stop,
                    source,
                    cleanup_errors,
                    job_handle,
                    final_deadline,
                    return_codes,
                )
            if durable_log is not None:
                cleanup_errors.extend(
                    cls._flush_durable_log(durable_log, final_deadline)
                )
            close_error = cls._windows_job_close(job_handle)
            if close_error is not None:
                cleanup_errors.append(close_error)
            cleanup_errors.extend(cls._close_process_resources(stack))
            cleanup_errors.extend(
                cls._restore_forwarding_handlers(previous_handlers)
            )
        return cls._process_exit_result(
            cmd,
            return_code,
            received_signals,
            (*failures, *cleanup_errors),
            nonfatal_diagnostics=tuple(live_diagnostics),
            timed_out=timed_out,
            legacy_timeout=legacy_timeout,
            legacy_timeout_seconds=legacy_timeout_seconds,
            timeout_exit_code=timeout_exit_code,
        )

    @staticmethod
    def _spawn_deadline_exhausted(
        absolute_deadline: float | None, grace_seconds: float
    ) -> bool:
        return (
            absolute_deadline is not None
            and time.monotonic() >= absolute_deadline - grace_seconds
        )

    @staticmethod
    def _block_forwarded_signals(
        handlers: list[
            tuple[
                signal.Signals,
                signal.Handlers | Callable[[int, FrameType | None], object],
            ]
        ],
    ) -> set[signal.Signals] | None:
        if os.name == "nt" or not hasattr(signal, "pthread_sigmask"):
            return None
        forwarded = tuple(signal_number for signal_number, _previous in handlers)
        return signal.pthread_sigmask(signal.SIG_BLOCK, forwarded)

    @staticmethod
    def _restore_signal_mask(
        previous_mask: set[signal.Signals] | None,
    ) -> set[signal.Signals] | None:
        if previous_mask is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        return None

    @classmethod
    def _start_root_waiter(
        cls,
        process: p.Cli.ProcessHandle,
        return_codes: list[int],
        failures: list[str],
        process_done: threading.Event,
        wake: threading.Event,
    ) -> threading.Thread:
        waiter = threading.Thread(
            target=cls._wait_for_root_process,
            args=(process, return_codes, failures, process_done, wake),
            name="flext-cli-process-waiter",
            daemon=False,
        )
        waiter.start()
        return waiter

    @classmethod
    def _start_output_pump(
        cls,
        source: BinaryIO,
        durable_log: BinaryIO,
        live_fd: int | None,
        failures: list[str],
        live_diagnostics: list[str],
        stop: threading.Event,
        wake: threading.Event,
    ) -> threading.Thread:
        pump = threading.Thread(
            target=cls._pump_process_output,
            args=(
                source,
                durable_log,
                live_fd,
                failures,
                live_diagnostics,
                stop,
                wake,
            ),
            name="flext-cli-process-output",
            daemon=False,
        )
        pump.start()
        return pump


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessExecutionMixin"]
