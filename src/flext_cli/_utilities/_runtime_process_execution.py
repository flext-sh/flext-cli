"""Resource ownership for one portable streamed process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import signal
import threading
import time
from typing import BinaryIO

from flext_cli import c, m, p, r, t
from flext_cli._utilities import (
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
    FlextCliUtilitiesRuntimeProcessOutputMixin,
    FlextCliUtilitiesRuntimeProcessResourcesMixin,
    FlextCliUtilitiesRuntimeProcessStartMixin,
    FlextCliUtilitiesRuntimeProcessTimingMixin,
)


class FlextCliUtilitiesRuntimeProcessExecutionMixin(
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
    FlextCliUtilitiesRuntimeProcessOutputMixin,
    FlextCliUtilitiesRuntimeProcessResourcesMixin,
    FlextCliUtilitiesRuntimeProcessStartMixin,
    FlextCliUtilitiesRuntimeProcessTimingMixin,
):
    """Own one child process and its streaming resources."""

    @classmethod
    def _execute_streamed_process(
        cls,
        request: m.Cli.RuntimeProcessRequest,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Own resources and complete one streamed child lifecycle.

        Returns:
            Captured bytes and the exact causal process outcome.

        """
        started = time.monotonic()
        timing_result = cls._resolve_process_timing(
            request,
            started,
            on_main_thread=threading.current_thread() is threading.main_thread(),
        )
        if timing_result.failure:
            return r[p.Cli.CommandBytesOutput].from_failure(timing_result)
        absolute_deadline, grace_seconds = timing_result.unwrap()
        state = m.Cli.RuntimeProcessState(final_deadline=absolute_deadline)
        try:
            cls._execute_lifecycle(request, state, absolute_deadline, grace_seconds)
        except (OSError, TypeError, ValueError) as exc:
            exc.add_note(r[str].fail(str(exc), exception=exc).error or str(exc))
            state.primary_error = exc
            if state.process is not None:
                signal_result = cls._signal_process_tree(
                    state.process,
                    signal.SIGKILL,
                    state.job_handle,
                    force=True,
                )
                if signal_result.failure:
                    exc.add_note(signal_result.error or "process signal failed")
        finally:
            cls._finalize_lifecycle(state)
        if state.primary_error is not None:
            return r[p.Cli.CommandBytesOutput].fail(
                f"{c.Cli.OUTPUT_EXECUTION_ERROR}: {state.primary_error}",
                exception=state.primary_error,
            )
        return cls._captured_process_result(
            state,
            max(0.0, time.monotonic() - started),
        )

    @classmethod
    def _execute_lifecycle(
        cls,
        request: m.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        absolute_deadline: float | None,
        grace_seconds: float,
    ) -> None:
        if threading.current_thread() is threading.main_thread():
            state.restore_handlers.extend(
                cls._install_forwarding_handlers(
                    state.received_signals,
                    state.forwarded_signals,
                    state.wake,
                ),
            )
        prepared_cmd = tuple(request.cmd)
        if state.received_signals:
            state.wake.set()
            return
        if request.output_path is not None:
            request.output_path.parent.mkdir(parents=True, exist_ok=True)
            state.durable_log = state.stack.enter_context(
                request.output_path.open("wb", buffering=0),
            )
        stdin_result = cls._prepare_streamed_stdin(state.stack, request.input_data)
        live_result = cls._prepare_live_descriptor(state.stack, live=request.live)
        if stdin_result.failure:
            state.failures.append(stdin_result.error or "stdin preparation failed")
        elif live_result.failure:
            state.failures.append(live_result.error or "live output preparation failed")
        elif state.received_signals:
            state.wake.set()
        elif cls._spawn_deadline_exhausted(absolute_deadline, grace_seconds):
            state.failures.append("process deadline exhausted before child spawn")
        else:
            start_result = cls._start_contained_process(
                prepared_cmd,
                request.cwd,
                request.env,
                stdin_result.value[0],
                options=m.Cli.RuntimeSpawnOptions(
                    capture_output=(
                        request.output_path is not None or request.capture_output
                    ),
                    combine_output=request.output_path is not None,
                ),
            )
            if start_result.failure:
                state.failures.append(start_result.error or "process start failed")
            else:
                owned_process, state.job_handle = start_result.unwrap()
                state.process = owned_process
                waiter = cls._attach_process_streams(
                    owned_process,
                    request,
                    state,
                    stdin_result.unwrap(),
                    live_result.value[0],
                )
                state.timed_out, state.final_deadline = cls._monitor_process(
                    owned_process,
                    state,
                    absolute_deadline,
                    grace_seconds,
                    progress=(live_result.value[1], request.heartbeat_seconds),
                )
                state.return_code = cls._reap_and_drain(owned_process, waiter, state)
                state.cleanup_complete = True

    @classmethod
    def _attach_process_streams(
        cls,
        process: p.Cli.ProcessHandle,
        request: m.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        stdin: t.Triple[BinaryIO | None, BinaryIO | None, bytes],
        live_fd: int | None,
    ) -> threading.Thread:
        """Attach child I/O without losing ownership on a partial failure.

        Returns:
            The root waiter already retained by the lifecycle state.

        """
        stdin_reader, stdin_writer, stdin_payload = stdin
        if stdin_reader is not None:
            try:
                stdin_reader.close()
            except (OSError, ValueError) as exc:
                state.failures.append(
                    r[str]
                    .fail(
                        f"parent stdin reader close error: {exc}",
                        exception=exc,
                    )
                    .error
                    or str(exc),
                )
        waiter = cls._start_root_waiter(
            process,
            state.return_codes,
            state.failures,
            state.process_done,
            state.wake,
        )
        state.waiter = waiter
        state.pump_streams.extend(
            cls._start_process_output(
                process,
                state,
                live_fd,
                capture_output=request.capture_output,
            ),
        )
        if stdin_writer is not None:
            input_thread = cls._start_input_pump(
                stdin_writer,
                stdin_payload,
                state.failures,
                state.wake,
            )
            state.input_pump = (input_thread, stdin_writer)
        return waiter

    @classmethod
    def _finalize_lifecycle(cls, state: m.Cli.RuntimeProcessState) -> None:
        if (
            state.process is not None
            and state.waiter is not None
            and not state.cleanup_complete
        ):
            state.return_code = cls._reap_and_drain(
                state.process,
                state.waiter,
                state,
            )
        if state.durable_log is not None:
            state.cleanup_errors.extend(cls._flush_durable_log(state.durable_log))
        close_error = cls._windows_job_close(state.job_handle)
        if close_error is not None:
            state.cleanup_errors.append(close_error)
        state.cleanup_errors.extend(cls._close_process_resources(state.stack))
        state.cleanup_errors.extend(
            cls._restore_forwarding_handlers(state.restore_handlers),
        )
        if state.primary_error is not None:
            for cleanup_error in state.cleanup_errors:
                state.primary_error.add_note(cleanup_error)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessExecutionMixin"]
