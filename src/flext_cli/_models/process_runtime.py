"""Parameter objects owned by the contained process lifecycle runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, Literal

from flext_core import m

from flext_cli import p, t


class FlextCliModelsProcessRuntime:
    """Lifecycle parameter objects exposed through ``m.Cli``."""

    class ProcessTreeSignal(m.FrozenModel):
        """One signal delivery to a complete owned process tree."""

        signal_number: int = m.Field(
            description="Native signal number delivered to the owned tree.",
        )
        force: bool = m.Field(
            description="Deliver an unconditional kill instead of the signal.",
        )

    class RuntimeProcessTiming(m.FrozenModel):
        """Resolved absolute deadline and termination reserve of one lifecycle."""

        absolute_deadline: float | None = m.Field(
            description="Monotonic instant the complete lifecycle must end by.",
        )
        grace_seconds: float = m.Field(
            ge=0.0,
            description="Reserve kept for interrupt, TERM, KILL, and drain phases.",
        )

    class RuntimeHeartbeat(m.FrozenModel):
        """Progress heartbeat emitted on the live descriptor while waiting."""

        descriptor: int | None = m.Field(
            description="Live descriptor receiving heartbeat lines.",
        )
        interval_seconds: float | None = m.Field(
            description="Interval between heartbeat lines; absent disables them.",
        )

    class RuntimeMonitorPhase(m.ArbitraryTypesModel):
        """Mutable escalation boundaries and sent phases of one monitor loop."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            validate_assignment=False,
        )
        timing: FlextCliModelsProcessRuntime.RuntimeProcessTiming = m.Field(
            description="Declared lifecycle deadline and termination reserve.",
        )
        heartbeat: FlextCliModelsProcessRuntime.RuntimeHeartbeat = m.Field(
            description="Live progress heartbeat emitted while waiting.",
        )
        lifecycle_deadline: float | None = m.Field(
            description="Deadline reported to cleanup once monitoring stops.",
        )
        soft_at: float | None = m.Field(
            description="Instant the timeout interrupt is delivered.",
        )
        term_at: float | None = m.Field(
            description="Instant the TERM phase is delivered.",
        )
        kill_at: float | None = m.Field(
            description="Instant the KILL phase is delivered.",
        )
        cleanup_at: float | None = m.Field(
            description="Instant monitoring yields to cleanup.",
        )
        heartbeat_at: float | None = m.Field(
            description="Instant the next heartbeat line is due.",
        )
        timed_out: bool = m.Field(
            default=False,
            description="Whether the timeout interrupt was delivered.",
        )
        forwarded_count: int = m.Field(
            default=0,
            description="Received operator signals already forwarded.",
        )
        timeout_interrupt_sent: bool = m.Field(
            default=False,
            description="Whether the timeout interrupt phase ran.",
        )
        term_sent: bool = m.Field(
            default=False,
            description="Whether a TERM phase was delivered.",
        )
        kill_sent: bool = m.Field(
            default=False,
            description="Whether a KILL phase was delivered.",
        )
        interrupt_mode: bool = m.Field(
            default=False,
            description="Whether an operator signal rescheduled the phases.",
        )

    class RuntimeOutputPlan(m.FrozenModel):
        """Live mirroring and capture policy for the child output pipes."""

        live_fds: tuple[int | None, int | None] = m.Field(
            description="Live stdout and stderr descriptors mirrored by the pumps.",
        )
        capture_output: bool = m.Field(
            description="Whether pump output is retained in the captured buffers.",
        )

    class RuntimeSpawnCommand(m.ImmutableValueModel):
        """Native argv, working directory, and environment of one child.

        Immutable value preset without string normalization: argv and
        environment reach the operating system exactly as given.
        """

        cmd: tuple[str, ...] = m.Field(
            description="Executable and ordered child arguments.",
        )
        cwd: t.Cli.TextPath | None = m.Field(
            description="Working directory for child execution.",
        )
        env: Mapping[str, str] | None = m.Field(
            description="Resolved child environment; absent inherits the parent.",
        )

    class RuntimePipeDrain(m.ArbitraryTypesModel):
        """One pipe pump joined, and its stream closed, during cleanup."""

        pump: t.Port[threading.Thread] = m.Field(
            exclude=True,
            description="Thread owning the pipe until its end of stream.",
        )
        stream: t.Port[p.Cli.RuntimeClosableStream] = m.Field(
            exclude=True,
            description="Stream closed when the pump outlives its deadline.",
        )
        direction: Literal["input", "output"] = m.Field(
            description="Pipe direction named in causal cleanup evidence.",
        )

    class ProcessIsolationSeal(m.FrozenModel):
        """Sealed launcher, compiled policy, and retained runtime roots."""

        launcher: int = m.Field(
            ge=0,
            description="Sealed descriptor carrying the authenticated launcher.",
        )
        policy: int = m.Field(
            ge=0,
            description="Sealed descriptor carrying the compiled native policy.",
        )
        runtime_descriptors: tuple[tuple[int, Path], ...] = m.Field(
            description="Retained directory descriptors and their declared roots.",
        )

    class NativeElfLayout(m.FrozenModel):
        """Byte order and word width of one immutable ELF image."""

        order: Literal["<", ">"] = m.Field(
            description="Struct byte-order prefix of the ELF data encoding.",
        )
        wide: bool = m.Field(
            description="Whether the image uses the 64-bit ELF class.",
        )


__all__: list[str] = ["FlextCliModelsProcessRuntime"]
