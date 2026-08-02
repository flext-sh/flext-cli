"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import BinaryIO, Protocol, runtime_checkable

from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_01 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart01,
)
from flext_core import p


class FlextCliProtocolsBase(FlextCliProtocolsBasePart01):
    """Implementation part for FlextCliProtocolsBase."""

    @runtime_checkable
    class Settings(p.Settings, FlextCliProtocolsBasePart01.CliSettings, Protocol):
        """Protocol for CLI runtime settings consumed by the public services.

        NOTE (multi-agent): settings are flat ``cli_*`` scalars (§2.6); the
        nested ``Cli`` branch and its pyrefly ``Final`` workaround were
        removed with it. The flat field contract comes from
        ``CliSettings`` (part_01) via protocol composition.
        """

        @property
        def debug(self) -> bool:
            """Check if debug mode is enabled."""
            ...

        @property
        def trace(self) -> bool:
            """Check if trace mode is enabled."""
            ...

        @classmethod
        def reset_for_testing(cls) -> None:
            """Reset the process-wide singleton (test isolation only)."""
            ...

    @runtime_checkable
    class CommandOutput(Protocol):
        """Minimal external command execution output contract."""

        @property
        def duration(self) -> float:
            """Command duration in seconds."""
            ...

        @property
        def exit_code(self) -> int:
            """Command exit code."""
            ...

        @property
        def stderr(self) -> str:
            """Command standard error."""
            ...

        @property
        def stdout(self) -> str:
            """Command standard output."""
            ...

    # mro-zf1s: binary command consumers type against p, never the model owner.
    @runtime_checkable
    class CommandBytesOutput(Protocol):
        """Byte-exact external command execution output contract."""

        @property
        def duration(self) -> float:
            """Command duration in seconds."""
            ...

        @property
        def exit_code(self) -> int:
            """Command exit code."""
            ...

        @property
        def stderr(self) -> bytes:
            """Command standard error as raw bytes."""
            ...

        @property
        def stdout(self) -> bytes:
            """Command standard output as raw bytes."""
            ...

    @runtime_checkable
    class ProcessDeadline(Protocol):
        """Absolute monotonic deadline for one complete process lifecycle."""

        @property
        def expires_at_monotonic(self) -> float:
            """Absolute time.monotonic expiry in seconds."""
            ...

        @property
        def termination_grace_seconds(self) -> float:
            """Reserved graceful termination and drain budget."""
            ...

        @property
        def timeout_exit_code(self) -> int:
            """Canonical exit code returned for deadline expiry."""
            ...

    @runtime_checkable
    class ProcessHandle(Protocol):
        """Structural subprocess handle used behind the public CLI facade."""

        @property
        def pid(self) -> int:
            """Operating-system process identifier."""
            ...

        @property
        def stdin(self) -> BinaryIO | None:
            """Binary standard-input pipe when configured."""
            ...

        @property
        def stdout(self) -> BinaryIO | None:
            """Binary combined-output pipe when configured."""
            ...

        def kill(self) -> None:
            """Force the process to exit."""
            ...

        def poll(self) -> int | None:
            """Return the exit status when available."""
            ...

        def send_signal(self, signal_number: int) -> None:
            """Send one platform signal to the process."""
            ...

        def wait(self, timeout: float | None = None) -> int:
            """Wait for the process within a bounded interval."""
            ...

    @runtime_checkable
    class ProcessLiveSink(Protocol):
        """Nonblocking live-output consumer fed by the durable reader."""

        def offer(self, chunk: bytes) -> None:
            """Offer one durable chunk without blocking the reader."""
            ...

    @runtime_checkable
    class ProcessLivePolicy(Protocol):
        """Validated bounded live relay policy."""

        @property
        def stream_chunk_bytes(self) -> int:
            """Durable reader chunk size."""
            ...

        @property
        def queue_capacity_chunks(self) -> int:
            """Maximum queued live chunks."""
            ...

        @property
        def relay_poll_seconds(self) -> float:
            """Interruptible relay polling interval."""
            ...


__all__: list[str] = ["FlextCliProtocolsBase"]
