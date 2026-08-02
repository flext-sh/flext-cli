"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import threading
from typing import TYPE_CHECKING, BinaryIO, Protocol, runtime_checkable

from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_04 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart04,
)

if TYPE_CHECKING:
    # Why (multi-agent): defer flext_cli import to break the __init__-time
    # circular import; t is annotation-only (PEP 563). Matches sibling part_03.
    from flext_cli import p, t


class FlextCliProtocolsBase(FlextCliProtocolsBasePart04):
    """Implementation part for FlextCliProtocolsBase."""

    @runtime_checkable
    class ProcessLiveDiagnostics(Protocol):
        """Live relay diagnostics retained through final cleanup."""

        @property
        def nonfatal(self) -> tuple[str, ...]:
            """Return the first live truncation reason, when present."""
            ...

        @property
        def cleanup(self) -> tuple[str, ...]:
            """Return every relay cleanup diagnostic."""
            ...

        @property
        def fatal(self) -> tuple[str, ...]:
            """Return residual relay ownership failures."""
            ...

    @runtime_checkable
    class ProcessLiveSession(
        FlextCliProtocolsBasePart04.ProcessLiveSink,
        Protocol,
    ):
        """Owned live relay retained until bounded finalization."""

        def finish(
            self,
            cleanup_deadline: float,
        ) -> FlextCliProtocolsBase.ProcessLiveDiagnostics:
            """Stop and reap the relay, returning cumulative diagnostics."""
            ...

    @runtime_checkable
    class YamlModule(Protocol):
        """Protocol for YAML serialization module interface."""

        def dump(self, data: t.JsonPayload, *, default_flow_style: bool = True) -> str:
            """Dump data as YAML string."""
            ...

    @runtime_checkable
    class ProcessOwnedState(Protocol):
        """Mutable ownership record for one streamed process lifecycle."""

        process: p.Cli.ProcessHandle | None
        pump: threading.Thread | None
        source: BinaryIO | None
        durable_log: BinaryIO | None
        live_session: p.Cli.ProcessLiveSession | None
        job_handle: int
        failures: list[str]
        live_diagnostics: list[str]
        cleanup_errors: list[str]
        return_code: int | None
        timed_out: bool
        final_deadline: float | None
        drain_at: float | None
        flush_at: float | None
        previous_handlers: list[t.Cli.SignalHandlerState]
        received_signals: list[int]
        pump_stop: threading.Event
        stack: contextlib.ExitStack


__all__: list[str] = ["FlextCliProtocolsBase"]
