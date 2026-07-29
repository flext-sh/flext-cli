"""Resource ownership for one portable streamed process lifecycle."""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path
from types import FrameType
from typing import BinaryIO

from flext_cli import c, p, r, t
from flext_cli._utilities._runtime_process_cleanup import (
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
)
from flext_cli._utilities._runtime_process_outcome import (
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
)


class FlextCliUtilitiesRuntimeProcessExecutionMixin(
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
):
    """Own one child process and its streaming resources."""

    @classmethod
    def _execute_streamed_process(
        cls,
        cmd: t.StrSequence,
        output_path: Path,
        cwd: t.Cli.TextPath | None,
        env: dict[str, str] | None,
        input_data: bytes | None,
        *,
        live: bool,
        absolute_deadline: float | None,
        grace_seconds: float,
        timeout_exit_code: int,
        legacy_timeout: bool,
        legacy_timeout_seconds: int | None,
    ) -> p.Result[int]:
        """Own resources and complete one streamed child lifecycle."""
        process: subprocess.Popen[bytes] | None = None
        pump: threading.Thread | None = None
        source: BinaryIO | None = None
        job_handle = 0
        failures: list[str] = []
        cleanup_errors: list[str] = []
        previous_handlers: list[
            tuple[
                signal.Signals,
                signal.Handlers | Callable[[int, FrameType | None], object],
            ]
        ] = []
        previous_signal_mask: set[signal.Signals] | None = None
        received_signals: list[int] = []
        pump_stop = threading.Event()
        try:
            if threading.current_thread() is threading.main_thread():
                previous_handlers = cls._install_forwarding_handlers(received_signals)
                forwarded = tuple(
                    signal_number for signal_number, _previous in previous_handlers
                )
                if os.name != "nt" and hasattr(signal, "pthread_sigmask"):
                    previous_signal_mask = signal.pthread_sigmask(
                        signal.SIG_BLOCK, forwarded
                    )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with contextlib.ExitStack() as stack:
                durable_log = stack.enter_context(output_path.open("wb", buffering=0))
                stdin_handle: BinaryIO | int = subprocess.DEVNULL
                if input_data is not None:
                    prepared_stdin = stack.enter_context(tempfile.TemporaryFile())
                    if prepared_stdin.write(input_data) != len(input_data):
                        return r[int].fail(
                            "execution error: stdin preparation was partial"
                        )
                    prepared_stdin.seek(0)
                    stdin_handle = prepared_stdin
                live_fd = os.dup(sys.stdout.fileno()) if live else None
                if live_fd is not None:
                    stack.callback(os.close, live_fd)
                    live_was_blocking = os.get_blocking(live_fd)
                    os.set_blocking(live_fd, False)
                    stack.callback(os.set_blocking, live_fd, live_was_blocking)
                creation_flags = 0
                if os.name == "nt":
                    creation_flags = int(
                        getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                    ) | int(getattr(subprocess, "CREATE_SUSPENDED", 0x00000004))
                process = subprocess.Popen(
                    list(cmd),
                    cwd=cwd,
                    stdin=stdin_handle,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=False,
                    bufsize=0,
                    env=env,
                    start_new_session=os.name != "nt",
                    creationflags=creation_flags,
                )
                job_result = cls._windows_job_create(process)
                if job_result.failure:
                    process.kill()
                    process.wait()
                    return r[int].fail(
                        job_result.error or "Windows Job Object assignment failed"
                    )
                job_handle = job_result.value
                resume_error = cls._windows_process_resume(process.pid)
                if resume_error is not None:
                    _ = cls._signal_process_tree(
                        process, signal.SIGKILL, job_handle, force=True
                    )
                    process.wait()
                    return r[int].fail(resume_error)
                if previous_signal_mask is not None:
                    signal.pthread_sigmask(signal.SIG_SETMASK, previous_signal_mask)
                    previous_signal_mask = None
                source = process.stdout
                if source is None:
                    return r[int].fail(
                        "execution error: combined output pipe unavailable"
                )
                stack.callback(source.close)
                os.set_blocking(source.fileno(), False)
                pump = threading.Thread(
                    target=cls._pump_process_output,
                    args=(source, durable_log, live_fd, failures, pump_stop),
                    name="flext-cli-process-output",
                    daemon=False,
                )
                pump.start()
                timed_out, final_deadline, drain_at, flush_at = cls._monitor_process(
                    process,
                    pump,
                    failures,
                    received_signals,
                    job_handle,
                    absolute_deadline,
                    grace_seconds,
                )
                return_code = cls._reap_and_drain(
                    process,
                    pump,
                    pump_stop,
                    source,
                    cleanup_errors,
                    job_handle,
                    drain_at,
                    flush_at,
                )
                try:
                    durable_log.flush()
                    os.fsync(durable_log.fileno())
                except (OSError, ValueError) as exc:
                    cleanup_errors.append(f"durable log flush error: {exc}")
                if final_deadline is not None and time.monotonic() > final_deadline:
                    cleanup_errors.append(
                        "process deadline expired before durable log flush"
                    )
                close_error = cls._windows_job_close(job_handle)
                job_handle = 0
                if close_error is not None:
                    cleanup_errors.append(close_error)
                return cls._process_exit_result(
                    cmd,
                    return_code,
                    received_signals,
                    (*failures, *cleanup_errors),
                    timed_out=timed_out,
                    legacy_timeout=legacy_timeout,
                    legacy_timeout_seconds=legacy_timeout_seconds,
                    timeout_exit_code=timeout_exit_code,
                )
        except c.EXC_OS_VALUE as exc:
            return r[int].fail(f"execution error: {exc}")
        finally:
            if previous_signal_mask is not None:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_signal_mask)
            cls._restore_forwarding_handlers(previous_handlers)
            if process is not None and process.poll() is None:
                _ = cls._signal_process_tree(
                    process, signal.SIGKILL, job_handle, force=True
                )
                with contextlib.suppress(subprocess.TimeoutExpired):
                    process.wait(timeout=cls._SIGNAL_CLEANUP_SECONDS)
            if pump is not None and pump.is_alive():
                pump_stop.set()
                pump.join(cls._SIGNAL_CLEANUP_SECONDS)
            _ = cls._windows_job_close(job_handle)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessExecutionMixin"]
