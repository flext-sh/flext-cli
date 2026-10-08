"""Absolute-deadline monitoring for streamed process execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import signal
import time

from flext_cli import c, p, t
from flext_cli._utilities import FlextCliUtilitiesRuntimeProcessGroupMixin
from flext_cli._utilities._runtime_models import FlextCliRuntimeProcessState


class FlextCliUtilitiesRuntimeProcessMonitorMixin(
    FlextCliUtilitiesRuntimeProcessGroupMixin,
):
    """Monitor one process group through events and one absolute deadline."""

    @classmethod
    def _monitor_process(
        cls,
        process: p.Cli.ProcessHandle,
        state: FlextCliRuntimeProcessState,
        absolute_deadline: float | None,
        grace_seconds: float,
        *,
        progress: t.Pair[int | None, float | None],
    ) -> t.Pair[bool, float | None]:
        """Forward signals and advance TERM/KILL phases without polling.

        Returns:
            The resulting ``t.Pair[bool, float | None]``.

        """
        lifecycle_deadline = absolute_deadline
        soft_at = cls._soft_boundary(absolute_deadline, grace_seconds)
        term_at = cls._phase_boundary(soft_at, grace_seconds, numerator=1)
        kill_at = cls._phase_boundary(soft_at, grace_seconds, numerator=2)
        cleanup_at = cls._phase_boundary(soft_at, grace_seconds, numerator=5)
        timed_out = False
        forwarded_count = 0
        timeout_interrupt_sent = False
        term_sent = False
        kill_sent = False
        interrupt_mode = False
        heartbeat_at = (
            time.monotonic() + progress[1]
            if progress[0] is not None and progress[1] is not None
            else None
        )
        while True:
            state.wake.clear()
            # Clear before observing completion: a waiter that finishes between
            # the observation and clear would otherwise lose its only wake-up.
            if state.process_done.is_set():
                break
            now = time.monotonic()
            if state.received_signals and not interrupt_mode:
                interrupt_mode = True
                lifecycle_deadline = cls._interrupt_deadline(now, absolute_deadline)
                reserve = max(0.0, lifecycle_deadline - now)
                soft_at = now
                term_at = cls._phase_boundary(now, reserve, numerator=1)
                kill_at = cls._phase_boundary(now, reserve, numerator=2)
                cleanup_at = cls._phase_boundary(now, reserve, numerator=5)
            forwarded_count, term_sent, kill_sent = cls._forward_received(
                process,
                state,
                forwarded_count,
                term_sent=term_sent,
                kill_sent=kill_sent,
            )
            if (
                heartbeat_at is not None
                and progress[1] is not None
                and now >= heartbeat_at
            ):
                cls._write_heartbeat(progress[0])
                heartbeat_at = now + progress[1]
            if state.failures and not kill_sent:
                cls._record_signal_error(
                    state.failures,
                    cls._signal_process_tree(
                        process,
                        signal.SIGKILL,
                        state.job_handle,
                        force=True,
                    ),
                )
                kill_sent = True
            if (
                soft_at is not None
                and now >= soft_at
                and not state.received_signals
                and not timeout_interrupt_sent
            ):
                timed_out = True
                cls._record_signal_error(
                    state.failures,
                    cls._signal_process_tree(
                        process,
                        signal.SIGINT,
                        state.job_handle,
                        force=False,
                    ),
                )
                timeout_interrupt_sent = True
            if term_at is not None and now >= term_at and not term_sent:
                cls._record_signal_error(
                    state.failures,
                    cls._signal_process_tree(
                        process,
                        signal.SIGTERM,
                        state.job_handle,
                        force=False,
                    ),
                )
                term_sent = True
            if kill_at is not None and now >= kill_at and not kill_sent:
                cls._record_signal_error(
                    state.failures,
                    cls._signal_process_tree(
                        process,
                        signal.SIGKILL,
                        state.job_handle,
                        force=True,
                    ),
                )
                kill_sent = True
            if cleanup_at is not None and now >= cleanup_at:
                break
            next_boundary = cls._next_boundary(
                now,
                soft_at if not timeout_interrupt_sent else None,
                term_at if not term_sent else None,
                kill_at if not kill_sent else None,
                cleanup_at,
                heartbeat_at,
            )
            state.wake.wait(
                None
                if next_boundary is None
                else max(0.0, next_boundary - time.monotonic()),
            )
        return timed_out, lifecycle_deadline

    @staticmethod
    def _write_heartbeat(progress_fd: int | None) -> None:
        if progress_fd is None:
            msg = "process heartbeat descriptor is unavailable"
            raise RuntimeError(msg)
        payload = f"{c.Cli.CLI_PROCESS_HEARTBEAT_MESSAGE}\n".encode(
            c.Cli.ENCODING_DEFAULT,
        )
        written = os.write(progress_fd, payload)
        if written != len(payload):
            msg = (
                "process heartbeat output write was incomplete: "
                f"{written}/{len(payload)} bytes"
            )
            raise OSError(msg)

    @staticmethod
    def _soft_boundary(
        absolute_deadline: float | None,
        grace_seconds: float,
    ) -> float | None:
        return (
            absolute_deadline - grace_seconds if absolute_deadline is not None else None
        )

    @staticmethod
    def _phase_boundary(
        start: float | None,
        reserve: float,
        *,
        numerator: int,
    ) -> float | None:
        return None if start is None else start + (reserve * numerator / 6.0)

    @staticmethod
    def _interrupt_deadline(now: float, absolute_deadline: float | None) -> float:
        local_deadline = now + 1.0
        return (
            min(local_deadline, absolute_deadline)
            if absolute_deadline is not None
            else local_deadline
        )

    @classmethod
    def _forward_received(
        cls,
        process: p.Cli.ProcessHandle,
        state: FlextCliRuntimeProcessState,
        forwarded_count: int,
        *,
        term_sent: bool,
        kill_sent: bool,
    ) -> t.Triple[int, bool, bool]:
        force_after_signals = 2
        while forwarded_count < len(state.received_signals):
            signal_number = state.received_signals[forwarded_count]
            force = forwarded_count >= force_after_signals
            forwarded_signal = (
                signal_number
                if forwarded_count == 0
                else signal.SIGKILL
                if force
                else signal.SIGTERM
            )
            cls._record_signal_error(
                state.failures,
                cls._signal_process_tree(
                    process,
                    forwarded_signal,
                    state.job_handle,
                    force=force,
                ),
            )
            forwarded_count += 1
            term_sent = term_sent or forwarded_signal == signal.SIGTERM
            kill_sent = kill_sent or force
        return forwarded_count, term_sent, kill_sent

    @staticmethod
    def _record_signal_error(
        failures: t.MutableSequenceOf[str],
        signal_result: p.Result[bool],
    ) -> None:
        if signal_result.failure:
            failures.append(signal_result.error or "process signal failed")

    @staticmethod
    def _next_boundary(now: float, *boundaries: float | None) -> float | None:
        pending = [value for value in boundaries if value is not None and value > now]
        return min(pending) if pending else None


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessMonitorMixin"]
