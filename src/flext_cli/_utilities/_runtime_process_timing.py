"""Deadline normalization for the canonical contained process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import shlex

from flext_cli import c, p, r, t
from flext_cli._utilities._runtime_models import FlextCliRuntimeProcessRequest


class FlextCliUtilitiesRuntimeProcessTimingMixin:
    """Resolve relative and absolute deadlines through one policy owner."""

    @staticmethod
    def _resolve_process_timing(
        request: FlextCliRuntimeProcessRequest,
        started: float,
        *,
        on_main_thread: bool,
    ) -> p.Result[t.Pair[float | None, float]]:
        timeout, deadline = request.timeout, request.deadline
        if timeout is not None and deadline is not None:
            return r[tuple[float | None, float]].fail(
                "timeout and deadline are mutually exclusive",
            )
        output_error = (
            FlextCliUtilitiesRuntimeProcessTimingMixin._process_output_policy_error(
                request,
                on_main_thread=on_main_thread,
            )
        )
        if output_error is not None:
            return r[tuple[float | None, float]].fail(output_error)
        absolute_deadline: float | None = None
        grace_seconds = 0.0

        if deadline is not None:
            absolute_deadline = deadline.expires_at_monotonic
            grace_seconds = deadline.termination_grace_seconds

        elif timeout is not None:
            if timeout <= 0:
                return r[tuple[float | None, float]].fail(
                    f"timeout {timeout}s: {shlex.join(list(request.cmd))}",
                )
            absolute_deadline = started + timeout
            grace_seconds = min(max(timeout * 0.1, 0.05), timeout * 0.5)
        if absolute_deadline is not None:
            remaining = absolute_deadline - started
            if remaining <= 0 or grace_seconds <= 0 or grace_seconds >= remaining:
                return r[tuple[float | None, float]].fail(
                    "process deadline must leave a positive grace reserve",
                )
        return r[tuple[float | None, float]].ok((absolute_deadline, grace_seconds))

    @staticmethod
    def _process_output_policy_error(
        request: FlextCliRuntimeProcessRequest,
        *,
        on_main_thread: bool,
    ) -> str | None:
        error: str | None = None
        if request.live and request.output_path is None:
            error = "live output requires a durable output path"
        elif request.heartbeat_seconds is not None and not request.live:
            error = "process heartbeat requires live output"
        elif request.heartbeat_seconds is not None and not (
            0 < request.heartbeat_seconds < c.Cli.CLI_PROCESS_HEARTBEAT_MAX_SECONDS
        ):
            error = (
                "process heartbeat interval must be greater than zero and below "
                f"{c.Cli.CLI_PROCESS_HEARTBEAT_MAX_SECONDS:g} seconds"
            )
        elif request.capture_output and request.output_path is not None:
            error = "captured and durable output are mutually exclusive"
        elif (request.live or request.deadline is not None) and not on_main_thread:
            error = (
                "live/deadline process execution requires the main interpreter thread"
            )
        return error


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessTimingMixin"]
