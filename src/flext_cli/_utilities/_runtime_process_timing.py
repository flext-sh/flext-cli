"""Deadline normalization for the canonical contained process lifecycle."""

from __future__ import annotations

import shlex

from flext_cli import c, p, r, t


class FlextCliUtilitiesRuntimeProcessTimingMixin:
    """Resolve relative and absolute deadlines through one policy owner."""

    @staticmethod
    def _resolve_process_timing(
        cmd: t.StrSequence,
        timeout: int | None,
        deadline: p.Cli.ProcessDeadline | None,
        started: float,
        *,
        capture_output: bool,
        has_output_path: bool,
        live: bool,
        heartbeat_seconds: float | None,
        on_main_thread: bool,
    ) -> p.Result[tuple[float | None, float]]:
        if timeout is not None and deadline is not None:
            return r[tuple[float | None, float]].fail(
                "timeout and deadline are mutually exclusive"
            )
        if live and not has_output_path:
            return r[tuple[float | None, float]].fail(
                "live output requires a durable output path"
            )
        if heartbeat_seconds is not None and not live:
            return r[tuple[float | None, float]].fail(
                "process heartbeat requires live output"
            )
        if heartbeat_seconds is not None and not (
            0 < heartbeat_seconds < c.Cli.CLI_PROCESS_HEARTBEAT_MAX_SECONDS
        ):
            return r[tuple[float | None, float]].fail(
                "process heartbeat interval must be greater than zero and below "
                f"{c.Cli.CLI_PROCESS_HEARTBEAT_MAX_SECONDS:g} seconds"
            )
        if capture_output and has_output_path:
            return r[tuple[float | None, float]].fail(
                "captured and durable output are mutually exclusive"
            )
        if (live or deadline is not None) and not on_main_thread:
            return r[tuple[float | None, float]].fail(
                "live/deadline process execution requires the main interpreter thread"
            )
        absolute_deadline: float | None = None
        grace_seconds = 0.0

        if deadline is not None:
            absolute_deadline = deadline.expires_at_monotonic
            grace_seconds = deadline.termination_grace_seconds

        elif timeout is not None:
            if timeout <= 0:
                return r[tuple[float | None, float]].fail(
                    f"timeout {timeout}s: {shlex.join(list(cmd))}"
                )
            absolute_deadline = started + timeout
            grace_seconds = min(max(timeout * 0.1, 0.05), timeout * 0.5)
        if absolute_deadline is not None:
            remaining = absolute_deadline - started
            if remaining <= 0 or grace_seconds <= 0 or grace_seconds >= remaining:
                return r[tuple[float | None, float]].fail(
                    "process deadline must leave a positive grace reserve"
                )
        return r[tuple[float | None, float]].ok((absolute_deadline, grace_seconds))


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessTimingMixin"]
