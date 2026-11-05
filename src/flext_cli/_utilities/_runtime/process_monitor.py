"""Absolute-deadline monitoring for streamed process execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import signal
import time
from collections.abc import MutableSequence

from flext_cli import c, m, p
from flext_cli._utilities._runtime import FlextCliUtilitiesRuntimeProcessGroup


class FlextCliUtilitiesRuntimeProcessMonitor(
    FlextCliUtilitiesRuntimeProcessGroup,
):
    """Monitor one process group through events and one absolute deadline."""

    @classmethod
    def _monitor_process(
        cls,
        process: p.Cli.ProcessHandle,
        state: p.Cli.RuntimeProcessState,
        timing: m.Cli.RuntimeProcessTiming,
        heartbeat: m.Cli.RuntimeHeartbeat,
    ) -> tuple[bool, float | None]:
        """Forward signals and advance TERM/KILL phases without polling.

        Returns:
            Whether the timeout interrupt ran, and the lifecycle deadline
            cleanup must honor.

        """
        phase = cls._initial_monitor_phase(timing, heartbeat)
        while True:
            state.wake.clear()
            # Clear before observing completion: a waiter that finishes between
            # the observation and clear would otherwise lose its only wake-up.
            if state.process_done.is_set():
                break
            now = time.monotonic()
            if state.received_signals and not phase.interrupt_mode:
                cls._enter_interrupt_mode(phase, now, timing.absolute_deadline)
            cls._forward_received(process, state, phase)
            cls._advance_heartbeat(phase, heartbeat, now)
            cls._advance_escalation(process, state, phase, now)
            if phase.cleanup_at is not None and now >= phase.cleanup_at:
                break
            next_boundary = cls._next_boundary(
                now,
                phase.soft_at if not phase.timeout_interrupt_sent else None,
                phase.term_at if not phase.term_sent else None,
                phase.kill_at if not phase.kill_sent else None,
                phase.cleanup_at,
                phase.heartbeat_at,
            )
            state.wake.wait(
                None
                if next_boundary is None
                else max(0.0, next_boundary - time.monotonic()),
            )
        return phase.timed_out, phase.lifecycle_deadline

    @classmethod
    def _initial_monitor_phase(
        cls,
        timing: m.Cli.RuntimeProcessTiming,
        heartbeat: m.Cli.RuntimeHeartbeat,
    ) -> m.Cli.RuntimeMonitorPhase:
        """Schedule the timeout phases inside the declared grace reserve.

        Returns:
            The phase boundaries before any operator signal arrives.

        """
        grace = timing.grace_seconds
        soft_at = cls._soft_boundary(timing.absolute_deadline, grace)
        return m.Cli.RuntimeMonitorPhase(
            lifecycle_deadline=timing.absolute_deadline,
            soft_at=soft_at,
            term_at=cls._phase_boundary(soft_at, grace, numerator=1),
            kill_at=cls._phase_boundary(soft_at, grace, numerator=2),
            cleanup_at=cls._phase_boundary(soft_at, grace, numerator=5),
            heartbeat_at=(
                time.monotonic() + heartbeat.interval_seconds
                if heartbeat.descriptor is not None
                and heartbeat.interval_seconds is not None
                else None
            ),
        )

    @classmethod
    def _enter_interrupt_mode(
        cls,
        phase: m.Cli.RuntimeMonitorPhase,
        now: float,
        absolute_deadline: float | None,
    ) -> None:
        """Reschedule every phase inside the local operator-interrupt reserve."""
        phase.interrupt_mode = True
        phase.lifecycle_deadline = cls._interrupt_deadline(now, absolute_deadline)
        reserve = max(0.0, phase.lifecycle_deadline - now)
        phase.soft_at = now
        phase.term_at = cls._phase_boundary(now, reserve, numerator=1)
        phase.kill_at = cls._phase_boundary(now, reserve, numerator=2)
        phase.cleanup_at = cls._phase_boundary(now, reserve, numerator=5)

    @classmethod
    def _advance_heartbeat(
        cls,
        phase: m.Cli.RuntimeMonitorPhase,
        heartbeat: m.Cli.RuntimeHeartbeat,
        now: float,
    ) -> None:
        """Emit one due heartbeat line and schedule the next one."""
        interval = heartbeat.interval_seconds
        if phase.heartbeat_at is None or interval is None or now < phase.heartbeat_at:
            return
        cls._write_heartbeat(heartbeat.descriptor)
        phase.heartbeat_at = now + interval

    @classmethod
    def _advance_escalation(
        cls,
        process: p.Cli.ProcessHandle,
        state: p.Cli.RuntimeProcessState,
        phase: m.Cli.RuntimeMonitorPhase,
        now: float,
    ) -> None:
        """Deliver every due failure, timeout, TERM, and KILL phase once."""
        kill = m.Cli.ProcessTreeSignal(signal_number=signal.SIGKILL, force=True)
        if state.failures and not phase.kill_sent:
            cls._deliver_tree_signal(process, state, kill)
            phase.kill_sent = True
        if not state.received_signals and cls._phase_due(
            phase.soft_at, now, sent=phase.timeout_interrupt_sent
        ):
            phase.timed_out = True
            cls._deliver_tree_signal(
                process,
                state,
                m.Cli.ProcessTreeSignal(signal_number=signal.SIGINT, force=False),
            )
            phase.timeout_interrupt_sent = True
        if cls._phase_due(phase.term_at, now, sent=phase.term_sent):
            cls._deliver_tree_signal(
                process,
                state,
                m.Cli.ProcessTreeSignal(signal_number=signal.SIGTERM, force=False),
            )
            phase.term_sent = True
        if cls._phase_due(phase.kill_at, now, sent=phase.kill_sent):
            cls._deliver_tree_signal(process, state, kill)
            phase.kill_sent = True

    @staticmethod
    def _phase_due(boundary: float | None, now: float, *, sent: bool) -> bool:
        """Report whether one unsent phase boundary has been reached.

        Returns:
            Whether the phase must be delivered now.

        """
        return boundary is not None and now >= boundary and not sent

    @classmethod
    def _deliver_tree_signal(
        cls,
        process: p.Cli.ProcessHandle,
        state: p.Cli.RuntimeProcessState,
        tree_signal: m.Cli.ProcessTreeSignal,
    ) -> None:
        """Signal the owned tree and retain a delivery failure as evidence."""
        cls._record_signal_error(
            state.failures,
            cls._signal_process_tree(process, state.job_handle, tree_signal),
        )

    @staticmethod
    def _write_heartbeat(progress_fd: int | None) -> None:
        if progress_fd is None:
            msg = "process heartbeat descriptor is unavailable"
            raise RuntimeError(msg)
        payload = f"{c.Cli.CLI_PROCESS_HEARTBEAT_MESSAGE}\n".encode(
            c.DEFAULT_ENCODING,
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
        state: p.Cli.RuntimeProcessState,
        phase: m.Cli.RuntimeMonitorPhase,
    ) -> None:
        """Forward each newly received operator signal, escalating repeats."""
        force_after_signals = 2
        while phase.forwarded_count < len(state.received_signals):
            signal_number = state.received_signals[phase.forwarded_count]
            force = phase.forwarded_count >= force_after_signals
            forwarded_signal = (
                signal_number
                if phase.forwarded_count == 0
                else signal.SIGKILL
                if force
                else signal.SIGTERM
            )
            cls._deliver_tree_signal(
                process,
                state,
                m.Cli.ProcessTreeSignal(signal_number=forwarded_signal, force=force),
            )
            phase.forwarded_count += 1
            phase.term_sent = phase.term_sent or forwarded_signal == signal.SIGTERM
            phase.kill_sent = phase.kill_sent or force

    @staticmethod
    def _record_signal_error(
        failures: MutableSequence[str],
        signal_result: p.Result[bool],
    ) -> None:
        if signal_result.failure:
            failures.append(signal_result.error or "process signal failed")

    @staticmethod
    def _next_boundary(now: float, *boundaries: float | None) -> float | None:
        pending = [value for value in boundaries if value is not None and value > now]
        return min(pending) if pending else None


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessMonitor"]
