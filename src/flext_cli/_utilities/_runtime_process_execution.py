"""Resource ownership for one portable streamed process lifecycle."""

from __future__ import annotations

import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import BinaryIO, cast

from flext_cli import c, m, p, settings, t
from flext_cli._utilities._runtime_live_session import (
    FlextCliUtilitiesRuntimeLiveSession,
)
from flext_cli._utilities._runtime_process_finalize import (
    FlextCliUtilitiesRuntimeProcessFinalizeMixin,
)
from flext_cli._utilities._runtime_process_state import (
    FlextCliUtilitiesRuntimeProcessState,
)


class FlextCliUtilitiesRuntimeProcessExecutionMixin(
    FlextCliUtilitiesRuntimeProcessFinalizeMixin,
):
    """Own one child process and its streaming resources."""

    @classmethod
    def _execute_streamed_process(
        cls,
        cmd: t.StrSequence,
        output_path: Path,
        cwd: t.Cli.TextPath | None,
        env: t.StrMapping | None,
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
        state: p.Cli.ProcessOwnedState = FlextCliUtilitiesRuntimeProcessState(
            absolute_deadline
        )
        try:
            if threading.current_thread() is threading.main_thread():
                state.previous_handlers = cls._install_forwarding_handlers(
                    state.received_signals
                )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            state.durable_log = state.stack.enter_context(
                output_path.open("wb", buffering=0)
            )
            stdin_handle: BinaryIO | int = subprocess.DEVNULL
            if input_data is not None:
                prepared_stdin = state.stack.enter_context(
                    tempfile.TemporaryFile()
                )
                if prepared_stdin.write(input_data) != len(input_data):
                    state.failures.append(
                        "execution error: stdin preparation was partial"
                    )
                else:
                    prepared_stdin.seek(0)
                    stdin_handle = prepared_stdin
            if live:
                live_policy = m.Cli.ProcessLivePolicy(
                    stream_chunk_bytes=settings.cli_process_stream_chunk_bytes,
                    queue_capacity_chunks=settings.cli_process_live_queue_chunks,
                    relay_poll_seconds=(
                        settings.cli_process_live_relay_poll_seconds
                    ),
                )
                relay_setup_deadline = (
                    absolute_deadline
                    if absolute_deadline is not None
                    else time.monotonic() + cls._SIGNAL_CLEANUP_SECONDS
                )
                live_result = FlextCliUtilitiesRuntimeLiveSession.start(
                    live_policy,
                    relay_setup_deadline,
                )
                if live_result.success:
                    state.live_session = live_result.value
                else:
                    state.live_diagnostics.append(
                        live_result.error
                        or "live output truncated: relay unavailable"
                    )
            if (
                absolute_deadline is not None
                and time.monotonic() >= absolute_deadline - grace_seconds
            ):
                state.failures.append(
                    "process deadline exhausted before child spawn"
                )
            if not state.failures:
                creation_flags = 0
                if os.name == "nt":
                    creation_flags = int(
                        getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                    ) | int(getattr(subprocess, "CREATE_SUSPENDED", 0x00000004))
                state.process = cast(
                    "p.Cli.ProcessHandle",
                    subprocess.Popen(
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
                    ),
                )
                job_result = cls._windows_job_create(state.process)
                if job_result.failure:
                    state.failures.append(
                        job_result.error or "Windows Job Object assignment failed"
                    )
                else:
                    state.job_handle = job_result.value
                    resume_error = cls._windows_process_resume(state.process.pid)
                    if resume_error is not None:
                        state.failures.append(resume_error)
                if not state.failures:
                    state.source = state.process.stdout
                    if state.source is None:
                        state.failures.append(
                            "execution error: combined output pipe unavailable"
                        )
                    else:
                        os.set_blocking(state.source.fileno(), False)
                        output_pump = threading.Thread(
                            target=cls._pump_process_output,
                            args=(
                                state.source,
                                state.durable_log,
                                state.live_session,
                                state.failures,
                                state.pump_stop,
                                settings.cli_process_stream_chunk_bytes,
                                settings.cli_process_live_relay_poll_seconds,
                            ),
                            name="flext-cli-process-output",
                            daemon=False,
                        )
                        output_pump.start()
                        state.pump = output_pump
                        (
                            state.timed_out,
                            state.final_deadline,
                            state.drain_at,
                            state.flush_at,
                        ) = cls._monitor_process(
                            state.process,
                            state.pump,
                            state.failures,
                            state.received_signals,
                            state.job_handle,
                            absolute_deadline,
                            grace_seconds,
                        )
        except c.EXC_OS_VALUE as exc:
            state.failures.append(f"execution error: {exc}")
        except RuntimeError as exc:
            state.failures.append(f"execution error: {exc}")
        finally:
            result = cls._finalize_streamed_process(
                cmd,
                state,
                legacy_timeout=legacy_timeout,
                legacy_timeout_seconds=legacy_timeout_seconds,
                timeout_exit_code=timeout_exit_code,
            )
        return result


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessExecutionMixin"]
