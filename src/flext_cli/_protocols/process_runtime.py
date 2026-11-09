# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/process_runtime
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._protocols import FlextCliProtocolsProcess


class FlextCliProtocolsProcessRuntime:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ProcessTreeSignal(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def signal_number(self) -> int:
            """Native signal number delivered to the owned tree."""
            ...

        @property
        def force(self) -> bool:
            """Deliver an unconditional kill instead of the signal."""
            ...

    @runtime_checkable
    class RuntimeProcessTiming(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def absolute_deadline(self) -> float | None:
            """Monotonic instant the complete lifecycle must end by."""
            ...

        @property
        def grace_seconds(self) -> float:
            """Reserve kept for interrupt, TERM, KILL, and drain phases."""
            ...

    @runtime_checkable
    class RuntimeHeartbeat(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def descriptor(self) -> int | None:
            """Live descriptor receiving heartbeat lines."""
            ...

        @property
        def interval_seconds(self) -> float | None:
            """Interval between heartbeat lines; absent disables them."""
            ...

    @runtime_checkable
    class RuntimeMonitorPhase(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def timing(self) -> FlextCliProtocolsProcessRuntime.RuntimeProcessTiming:
            """Declared lifecycle deadline and termination reserve."""
            ...

        @property
        def heartbeat(self) -> FlextCliProtocolsProcessRuntime.RuntimeHeartbeat:
            """Live progress heartbeat emitted while waiting."""
            ...

        lifecycle_deadline: float | None
        soft_at: float | None
        term_at: float | None
        kill_at: float | None
        cleanup_at: float | None
        heartbeat_at: float | None
        timed_out: bool
        forwarded_count: int
        timeout_interrupt_sent: bool
        term_sent: bool
        kill_sent: bool
        interrupt_mode: bool

    @runtime_checkable
    class RuntimeOutputPlan(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def live_fds(self) -> tuple[int | None, int | None]:
            """Live stdout and stderr descriptors mirrored by the pumps."""
            ...

        @property
        def capture_output(self) -> bool:
            """Whether pump output is retained in the captured buffers."""
            ...

    @runtime_checkable
    class RuntimeSpawnCommand(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def cmd(self) -> tuple[str, ...]:
            """Executable and ordered child arguments."""
            ...

        @property
        def cwd(self) -> t.Cli.TextPath | None:
            """Working directory for child execution."""
            ...

        @property
        def env(self) -> Mapping[str, str] | None:
            """Resolved child environment; absent inherits the parent."""
            ...

    @runtime_checkable
    class RuntimePipeDrain(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        pump: threading.Thread
        stream: FlextCliProtocolsProcess.RuntimeClosableStream
        direction: Literal["input", "output"]

    @runtime_checkable
    class ProcessIsolationSeal(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def launcher(self) -> int:
            """Sealed descriptor carrying the authenticated launcher."""
            ...

        @property
        def policy(self) -> int:
            """Sealed descriptor carrying the compiled native policy."""
            ...

        @property
        def runtime_descriptors(self) -> tuple[tuple[int, Path], ...]:
            """Retained directory descriptors and their declared roots."""
            ...

    @runtime_checkable
    class NativeElfLayout(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def order(self) -> Literal["<", ">"]:
            """Struct byte-order prefix of the ELF data encoding."""
            ...

        @property
        def wide(self) -> bool:
            """Whether the image uses the 64-bit ELF class."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsProcessRuntime",
]
