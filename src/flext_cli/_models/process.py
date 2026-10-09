"""Canonical launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar

from flext_cli import p, t
from flext_core import m


class FlextCliModelsProcess:
    """Process input declarations exposed through ``m.Cli``."""

    class ProcessOptions(m.ArbitraryTypesModel):
        """Child input, environment, and durable-output execution options."""

        env: t.StrMapping | None = m.Field(
            default=None,
            description="Environment overrides for the child process.",
        )
        remove_env_keys: t.StrSequence = m.Field(
            default=(),
            description="Environment keys to remove before child execution.",
        )
        input_data: str | bytes | None = m.Field(
            default=None,
            description="Text or byte payload supplied to child stdin.",
        )
        live: bool = m.Field(
            default=False,
            description="Mirror child output to live sinks.",
        )
        heartbeat_seconds: float | None = m.Field(
            default=None,
            description="Interval between live progress heartbeats.",
        )
        deadline: p.Cli.ProcessDeadline | None = m.Field(
            default=None,
            description="Absolute deadline and termination grace policy.",
        )
        pass_fds: t.InstanceOfSequence[int] = m.Field(
            default=(),
            description="File descriptors inherited by the child process.",
        )

    class RuntimeProcessRequest(m.ArbitraryTypesModel):
        """Resolved launch inputs shared by preparation and process creation."""

        # Borrow the sequence: iteration belongs after signal handlers are installed.
        cmd: t.InstanceOfSequence[str] = m.Field(
            description="Executable and ordered child arguments.",
        )
        output_path: Path | None = m.Field(
            default=None,
            description="Destination for the durable combined output log.",
        )
        cwd: t.Cli.TextPath | None = m.Field(
            default=None,
            description="Working directory for child execution.",
        )
        env: t.StrMapping | None = m.Field(
            default=None,
            description="Resolved environment for child execution.",
        )
        input_data: str | bytes | None = m.Field(
            default=None,
            description="Text or byte payload supplied to child stdin.",
        )
        capture_output: bool = m.Field(
            default=True,
            description="Retain child stdout and stderr in memory.",
        )
        live: bool = m.Field(
            default=False,
            description="Mirror child output to live sinks.",
        )
        heartbeat_seconds: float | None = m.Field(
            default=None,
            description="Interval between live progress heartbeats.",
        )
        timeout: int | None = m.Field(
            default=None,
            description="Relative child execution timeout in seconds.",
        )
        deadline: p.Cli.ProcessDeadline | None = m.Field(
            default=None,
            description="Absolute deadline and termination grace policy.",
        )

    class RuntimeProcessState(m.ArbitraryTypesModel):
        """Mutable ownership and causal evidence for exactly one lifecycle."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            validate_assignment=False,
        )
        process: p.Cli.ProcessHandle | None = m.Field(
            default=None,
            description="Owned root child process handle.",
        )
        waiter: threading.Thread | None = m.Field(
            default=None,
            description="Thread responsible for reaping the root child.",
        )
        durable_log: p.Cli.RuntimeBinaryStream | None = m.Field(
            default=None,
            description="Owned stream for durable combined child output.",
        )
        job_handle: int = m.Field(
            default=0,
            description="Windows job handle owning the child boundary.",
        )
        failures: t.MutableSequenceOf[str] = m.Field(
            default_factory=list,
            description="Causal failures collected during execution.",
        )
        cleanup_errors: t.MutableSequenceOf[str] = m.Field(
            default_factory=list,
            description="Failures collected while releasing resources.",
        )
        restore_handlers: t.MutableSequenceOf[Callable[[], None]] = m.Field(
            default_factory=list,
            description="Callbacks restoring the parent signal handlers.",
        )
        forwarded_signals: t.MutableSequenceOf[int] = m.Field(
            default_factory=list,
            description="Signal numbers registered for forwarding.",
        )
        received_signals: t.MutableSequenceOf[int] = m.Field(
            default_factory=list,
            description="Parent signals received during this lifecycle.",
        )
        return_codes: t.MutableSequenceOf[int] = m.Field(
            default_factory=list,
            description="Root child return codes recorded by the waiter.",
        )
        stdout_output: bytearray = m.Field(
            default_factory=bytearray,
            description="Mutable byte-exact captured stdout buffer.",
        )
        stderr_output: bytearray = m.Field(
            default_factory=bytearray,
            description="Mutable byte-exact captured stderr buffer.",
        )
        pump_streams: t.MutableSequenceOf[
            t.Pair[threading.Thread, p.Cli.RuntimeClosableStream]
        ] = m.Field(
            default_factory=list,
            description="Owned output pump threads paired with their source streams.",
        )
        input_pump: tuple[threading.Thread, p.Cli.RuntimeClosableStream] | None = (
            m.Field(
                default=None,
                description="Owned stdin pump thread paired with its sink stream.",
            )
        )
        pump_stop: threading.Event = m.Field(
            default_factory=threading.Event,
            description="Request for output pumps to stop.",
        )
        process_done: threading.Event = m.Field(
            default_factory=threading.Event,
            description="Notification that the root was reaped.",
        )
        wake: threading.Event = m.Field(
            default_factory=threading.Event,
            description="Notification of new lifecycle evidence.",
        )
        stack: contextlib.ExitStack = m.Field(
            default_factory=contextlib.ExitStack,
            description="Owner of lifecycle resource cleanup.",
        )
        return_code: int | None = m.Field(
            default=None,
            description="Final observed root child return code.",
        )
        timed_out: bool = m.Field(
            default=False,
            description="Whether child execution exhausted its deadline.",
        )
        final_deadline: float | None = m.Field(
            default=None,
            description="Monotonic deadline bounding final lifecycle cleanup.",
        )
        cleanup_complete: bool = m.Field(
            default=False,
            description="Whether child reaping and output draining completed.",
        )
        primary_error: Exception | None = m.Field(
            default=None,
            description="Primary exception retaining causal cleanup notes.",
        )

    class RuntimeOutputTarget(m.ArbitraryTypesModel):
        """Destinations for one byte-exact output pump."""

        durable_log: p.Cli.RuntimeBinaryStream | None = m.Field(
            default=None,
            description="Durable sink receiving byte-exact child output.",
        )
        captured_output: bytearray | None = m.Field(
            default=None,
            description="Mutable buffer retaining captured child output.",
        )
        live_fd: int | None = m.Field(
            default=None,
            description="Descriptor receiving mirrored live child output.",
        )

    class RuntimeSpawnOptions(m.ArbitraryTypesModel):
        """Pipe and platform creation policy for one child."""

        capture_output: bool = m.Field(
            description="Create pipes for capturing child output.",
        )
        combine_output: bool = m.Field(
            description="Combine child stderr into its stdout pipe.",
        )
        creation_flags: int = m.Field(
            default=0,
            description="Platform flags used when creating the child process.",
        )


__all__: list[str] = ["FlextCliModelsProcess"]
