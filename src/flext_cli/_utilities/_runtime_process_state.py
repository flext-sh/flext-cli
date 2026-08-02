"""Typed mutable ownership state for one streamed process lifecycle."""

from __future__ import annotations

import contextlib
import threading
from typing import BinaryIO

from flext_cli import p, t


class FlextCliUtilitiesRuntimeProcessState:
    """Keep every resource and diagnostic under one explicit owner."""

    __slots__ = (
        "cleanup_errors",
        "drain_at",
        "durable_log",
        "failures",
        "final_deadline",
        "flush_at",
        "job_handle",
        "live_diagnostics",
        "live_session",
        "previous_handlers",
        "process",
        "pump",
        "pump_stop",
        "received_signals",
        "return_code",
        "source",
        "stack",
        "timed_out",
    )

    def __init__(self, absolute_deadline: float | None) -> None:
        self.process: p.Cli.ProcessHandle | None = None
        self.pump: threading.Thread | None = None
        self.source: BinaryIO | None = None
        self.durable_log: BinaryIO | None = None
        self.live_session: p.Cli.ProcessLiveSession | None = None
        self.job_handle = 0
        self.failures: list[str] = []
        self.live_diagnostics: list[str] = []
        self.cleanup_errors: list[str] = []
        self.return_code: int | None = None
        self.timed_out = False
        self.final_deadline = absolute_deadline
        self.drain_at: float | None = None
        self.flush_at: float | None = None
        self.previous_handlers: list[t.Cli.SignalHandlerState] = []
        self.received_signals: list[int] = []
        self.pump_stop = threading.Event()
        self.stack = contextlib.ExitStack()


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessState"]
