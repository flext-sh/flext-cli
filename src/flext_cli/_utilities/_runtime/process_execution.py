"""Resource ownership for one portable streamed process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import signal
import threading
import time
from typing import BinaryIO, override

from flext_core import r

from flext_cli import c, m, p
from flext_cli._utilities._runtime import (
    FlextCliUtilitiesRuntimeProcessCleanup,
    FlextCliUtilitiesRuntimeProcessOutput,
    FlextCliUtilitiesRuntimeProcessResources,
    FlextCliUtilitiesRuntimeProcessStart,
    FlextCliUtilitiesRuntimeProcessTiming,
)
from flext_cli._utilities._runtime.process_isolation import (
    FlextCliUtilitiesRuntimeProcessIsolation,
)


class FlextCliUtilitiesRuntimeProcessExecution(
    FlextCliUtilitiesRuntimeProcessCleanup,
    FlextCliUtilitiesRuntimeProcessIsolation,
    FlextCliUtilitiesRuntimeProcessOutput,
    FlextCliUtilitiesRuntimeProcessResources,
    FlextCliUtilitiesRuntimeProcessStart,
    FlextCliUtilitiesRuntimeProcessTiming,
):
    """Own one child process and its streaming resources."""

    @classmethod
    @override
    def _execute_streamed_process(
        cls,
        request: p.Cli.RuntimeProcessRequest,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Own resources and complete one streamed child lifecycle.

        Returns:
            Captured bytes and the exact causal process outcome.

        """
        started = time.monotonic()
        timing_result = cls._resolve_process_timing(
            request,
            started,
            on_main_thread=(
                threading.current_thread() is threading.main_thread()
                or request.signal_wave is not None
            ),
        )
        if timing_result.failure:
            return r[p.Cli.CommandBytesOutput].from_failure(timing_result)
        timing = timing_result.unwrap()
        state = m.Cli.RuntimeProcessState(final_deadline=timing.absolute_deadline)
        interrupted: BaseException | None = None
        try:
            cls._execute_lifecycle(request, state, timing)
        except (OSError, TypeError, ValueError) as exc:
            exc.add_note(r[str].fail(str(exc), exception=exc).error or str(exc))
            state.primary_error = exc
            if state.process is not None:
                signal_result = cls._signal_process_tree(
                    state.process,
                    state.job_handle,
                    m.Cli.ProcessTreeSignal(signal_number=signal.SIGKILL, force=True),
                )
                if signal_result.failure:
                    exc.add_note(signal_result.error or "process signal failed")
        except BaseException as exc:
            interrupted = exc
            raise
        finally:
            try:
                cls._finalize_lifecycle(state, interrupted=interrupted)
            except BaseException as cleanup_exception:
                if interrupted is None:
                    raise
                interrupted.add_note(
                    f"process cleanup failed: {cleanup_exception}; "
                    f"execution errors={state.failures}; "
                    f"cleanup errors={state.cleanup_errors}"
                )
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
        request: p.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        timing: p.Cli.RuntimeProcessTiming,
    ) -> None:
        if threading.current_thread() is threading.main_thread():
            state.restore_handlers.extend(
                cls._install_forwarding_handlers(state.received_signals, state.wake),
            )
            state.forwarded_signals.extend(
                int(signal_number) for signal_number in cls.process_forwarded_signals()
            )
        elif request.signal_wave is not None:
            state.restore_handlers.append(
                request.signal_wave.subscribe(state.received_signals, state.wake),
            )
        if state.received_signals:
            state.wake.set()
            return
        isolated = cls._prepare_process_isolation(
            request, state, tuple(request.cmd), timing
        )
        if isolated is None:
            return
        prepared_cmd, child_env, inherited = isolated
        cls._open_durable_log_destinations(state, request)
        stdin_result = cls._prepare_streamed_stdin(state.stack, request.input_data)
        live_result = cls._prepare_live_descriptor(state.stack, live=request.live)
        if stdin_result.failure:
            state.failures.append(stdin_result.error or "stdin preparation failed")
        elif live_result.failure:
            state.failures.append(live_result.error or "live output preparation failed")
        elif state.received_signals:
            state.wake.set()
        elif cls._spawn_deadline_exhausted(
            timing.absolute_deadline, timing.grace_seconds
        ):
            state.failures.append("process deadline exhausted before child spawn")
        else:
            start_result = cls._start_contained_process(
                m.Cli.RuntimeSpawnCommand(
                    cmd=prepared_cmd, cwd=request.cwd, env=child_env
                ),
                stdin_result.value[0],
                options=m.Cli.RuntimeSpawnOptions(
                    capture_output=(
                        request.output_path is not None or request.capture_output
                    ),
                    combine_output=(
                        request.output_path is not None and request.stderr_path is None
                    ),
                    pass_fds=inherited,
                    stdin_mode="inherit" if request.inherit_stdin else "devnull",
                ),
            )
            if start_result.failure:
                state.failures.append(start_result.error or "process start failed")
            else:
                owned_process, state.job_handle = start_result.unwrap()
                state.process = owned_process
                waiter = cls._attach_process_streams(
                    owned_process,
                    state,
                    stdin_result.unwrap(),
                    m.Cli.RuntimeOutputPlan(
                        live_fds=live_result.value,
                        capture_output=request.capture_output,
                    ),
                )
                state.timed_out, state.final_deadline = cls._monitor_process(
                    owned_process,
                    state,
                    timing,
                    m.Cli.RuntimeHeartbeat(
                        descriptor=live_result.value[1],
                        interval_seconds=request.heartbeat_seconds,
                    ),
                )
                state.return_code = cls._reap_and_drain(owned_process, waiter, state)
                state.cleanup_complete = True

    @classmethod
    def _open_durable_log_destinations(
        cls, state: m.Cli.RuntimeProcessState, request: p.Cli.RuntimeProcessRequest
    ) -> None:
        """Create and retain unbuffered durable sinks on the lifecycle stack."""
        destinations = (request.output_path, request.stderr_path)
        for destination in destinations:
            if destination is not None:
                destination.parent.mkdir(parents=True, exist_ok=True)
        state.durable_log, state.durable_stderr = (
            state.stack.enter_context(destination.open("wb", buffering=0))
            if destination is not None
            else None
            for destination in destinations
        )

    @classmethod
    def _attach_process_streams(
        cls,
        process: p.Cli.ProcessHandle,
        state: m.Cli.RuntimeProcessState,
        stdin: tuple[BinaryIO | None, BinaryIO | None, bytes],
        output: p.Cli.RuntimeOutputPlan,
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
        waiter = cls._start_root_waiter(process, state)
        state.waiter = waiter
        state.pump_streams.extend(
            cls._start_process_output(process, state, output),
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
    def _finalize_lifecycle(
        cls,
        state: m.Cli.RuntimeProcessState,
        *,
        interrupted: BaseException | None = None,
    ) -> None:
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
        for stream in (state.durable_log, state.durable_stderr):
            if stream is not None:
                state.cleanup_errors.extend(cls._flush_durable_log(stream))
        close_error = cls._windows_job_close(state.job_handle)
        if close_error is not None:
            state.cleanup_errors.append(close_error)
        state.cleanup_errors.extend(cls._close_process_resources(state.stack))
        state.cleanup_errors.extend(
            cls._restore_forwarding_handlers(state.restore_handlers),
        )
        primary_error = interrupted if interrupted is not None else state.primary_error
        if primary_error is not None:
            for diagnostic in (*state.failures, *state.cleanup_errors):
                primary_error.add_note(diagnostic)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessExecution"]
