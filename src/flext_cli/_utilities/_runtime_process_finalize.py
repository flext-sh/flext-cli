"""Single fail-closed completion path for streamed process execution."""

from __future__ import annotations

import os
import time

from flext_cli import c, p, t
from flext_cli._utilities._runtime_process_cleanup import (
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
)
from flext_cli._utilities._runtime_process_outcome import (
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
)


class FlextCliUtilitiesRuntimeProcessFinalizeMixin(
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
):
    """Finalize all owned resources before restoring operator handlers."""

    @classmethod
    def _finalize_streamed_process(
        cls,
        cmd: t.StrSequence,
        state: p.Cli.ProcessOwnedState,
        *,
        legacy_timeout: bool,
        legacy_timeout_seconds: int | None,
        timeout_exit_code: int,
    ) -> p.Result[int]:
        """Complete cleanup, prove zero ownership, then normalize one result."""
        cleanup_deadline = (
            state.final_deadline
            if state.final_deadline is not None
            else time.monotonic() + cls._SIGNAL_CLEANUP_SECONDS
        )
        try:
            cls._finalize_owned_process_resources(state, cleanup_deadline)
        except c.EXC_OS_VALUE as exc:
            state.cleanup_errors.append(f"unexpected cleanup error: {exc}")
        except RuntimeError as exc:
            state.cleanup_errors.append(f"unexpected cleanup error: {exc}")
        finally:
            state.cleanup_errors.extend(
                cls._restore_forwarding_handlers(state.previous_handlers)
            )
        if (
            state.final_deadline is not None
            and time.monotonic() > state.final_deadline
        ):
            state.cleanup_errors.append(
                "complete process lifecycle exceeded its hard deadline"
            )
        return cls._process_exit_result(
            cmd,
            state.return_code,
            state.received_signals,
            (*state.failures, *state.cleanup_errors),
            tuple(state.live_diagnostics),
            timed_out=state.timed_out,
            legacy_timeout=legacy_timeout,
            legacy_timeout_seconds=legacy_timeout_seconds,
            timeout_exit_code=timeout_exit_code,
        )

    @classmethod
    def _finalize_owned_process_resources(
        cls,
        state: p.Cli.ProcessOwnedState,
        cleanup_deadline: float,
    ) -> None:
        """Release every owned process resource before handler restoration."""
        process = state.process
        if process is not None:
            try:
                state.return_code = cls._reap_and_drain(
                    process,
                    state.pump,
                    state.pump_stop,
                    state.source,
                    state.cleanup_errors,
                    state.job_handle,
                    state.drain_at,
                    state.flush_at,
                    cleanup_deadline,
                )
            except c.EXC_OS_VALUE as exc:
                state.cleanup_errors.append(f"process cleanup error: {exc}")
            except RuntimeError as exc:
                state.cleanup_errors.append(f"process cleanup error: {exc}")
        if state.source is not None:
            try:
                state.source.close()
            except (OSError, ValueError) as exc:
                state.cleanup_errors.append(f"combined output close error: {exc}")
        if state.live_session is not None:
            try:
                live_completion = state.live_session.finish(cleanup_deadline)
                state.live_diagnostics.extend(live_completion.nonfatal)
                state.cleanup_errors.extend(live_completion.cleanup)
                state.cleanup_errors.extend(live_completion.fatal)
            except c.EXC_OS_VALUE as exc:
                state.cleanup_errors.append(f"live relay cleanup error: {exc}")
            except RuntimeError as exc:
                state.cleanup_errors.append(f"live relay cleanup error: {exc}")
        if state.durable_log is not None:
            try:
                state.durable_log.flush()
                os.fsync(state.durable_log.fileno())
            except (OSError, ValueError) as exc:
                state.cleanup_errors.append(f"durable log flush error: {exc}")
        if process is not None:
            try:
                if process.poll() is None:
                    state.cleanup_errors.append(
                        "root process remained alive before return"
                    )
                if state.pump is not None and state.pump.is_alive():
                    state.cleanup_errors.append(
                        "durable output reader remained alive before return"
                    )
                boundary = cls._process_boundary_empty(
                    process.pid, state.job_handle
                )
                if boundary.failure:
                    state.cleanup_errors.append(
                        boundary.error or "owned process-boundary proof failed"
                    )
                elif not boundary.value:
                    state.cleanup_errors.append(
                        "owned process boundary remained active before Job close"
                    )
            except c.EXC_OS_VALUE as exc:
                state.cleanup_errors.append(f"process ownership proof error: {exc}")
            except RuntimeError as exc:
                state.cleanup_errors.append(f"process ownership proof error: {exc}")
        try:
            close_error = cls._windows_job_close(state.job_handle)
        except c.EXC_OS_VALUE as exc:
            close_error = f"Windows Job close error: {exc}"
        except RuntimeError as exc:
            close_error = f"Windows Job close error: {exc}"
        state.job_handle = 0
        if close_error is not None:
            state.cleanup_errors.append(close_error)
        try:
            state.stack.close()
        except c.EXC_OS_VALUE as exc:
            state.cleanup_errors.append(f"resource close error: {exc}")


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessFinalizeMixin"]
