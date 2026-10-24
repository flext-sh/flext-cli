"""Read-only launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import FrameType
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Buffer
    from pathlib import Path

    from flext_core import p

    from flext_cli import t
    from flext_cli._models.process import FlextCliModelsProcess
    from flext_cli._protocols._base import FlextCliProtocolsBasePart02


class FlextCliProtocolsProcess:
    """Structural launch and managed-child contracts exposed through ``p.Cli``."""

    @runtime_checkable
    class ParentSignalObserver(Protocol):
        """Observe interruption without taking over the owned child lifecycle."""

        def on_operator_signal(self, signum: int, frame: FrameType | None) -> None:
            """Capture signal evidence without invoking a terminating action."""
            ...

    @runtime_checkable
    class ManagedProcess(Protocol):
        """The existing managed child handle, independent of its utility owner."""

        @property
        def pid(self) -> int:
            """Operating-system child identifier."""
            ...

        @property
        def returncode(self) -> int | None:
            """Observed child exit code, absent while it runs."""
            ...

        @property
        def cwd(self) -> Path | None:
            """Declared child working directory."""
            ...

        @property
        def env(self) -> t.StrMapping | None:
            """Read-only child environment overrides."""
            ...

        @property
        def stdout(self) -> str:
            """Decoded standard output collected by the handle."""
            ...

        @property
        def stderr(self) -> str:
            """Decoded standard error collected by the handle."""
            ...

        def poll(self) -> int | None:
            """Observe child completion without waiting."""
            ...

        def terminate(self) -> p.Result[bool]:
            """Signal the owned child or process group to finish."""
            ...

        def kill(self) -> p.Result[bool]:
            """Force the owned child or process group to stop."""
            ...

        def wait(self, timeout: float | None = None) -> p.Result[int]:
            """Reap the child and preserve its output and exit code."""
            ...

        def stdout_read_until(
            self,
            delimiter: bytes,
            *,
            timeout: float,
        ) -> p.Result[bytes]:
            """Read through the delimiter within the supplied deadline."""
            ...

    @runtime_checkable
    class RuntimeClosableStream(Protocol):
        """The cleanup capability shared by owned input and output streams."""

        def close(self) -> None:
            """Release the stream."""
            ...

    @runtime_checkable
    class RuntimeBinaryStream(RuntimeClosableStream, Protocol):
        """Opaque durable sink, retained by identity rather than serialized."""

        def write(self, data: Buffer, /) -> int | None:
            """Write bytes to the sink."""
            ...

        def flush(self) -> None:
            """Flush buffered bytes."""
            ...

        def fileno(self) -> int:
            """Return the underlying descriptor."""
            ...

    @runtime_checkable
    class ProcessOptions(Protocol):
        """Read-only child input, environment, and durable-output options."""

        @property
        def env(self) -> t.StrMapping | None:
            """Environment overrides for the child process."""
            ...

        @property
        def remove_env_keys(self) -> t.StrSequence:
            """Environment keys to remove before child execution."""
            ...

        @property
        def inherit_environment(self) -> bool:
            """Whether execution overlays the inherited host environment."""
            ...

        @property
        def input_data(self) -> str | bytes | None:
            """Text or byte payload supplied to child stdin."""
            ...

        @property
        def live(self) -> bool:
            """Whether child output is mirrored to live sinks."""
            ...

        @property
        def heartbeat_seconds(self) -> float | None:
            """Interval between live progress heartbeats."""
            ...

        @property
        def deadline(self) -> FlextCliProtocolsBasePart02.ProcessDeadline | None:
            """Absolute deadline and termination grace policy."""
            ...

        @property
        def pass_fds(self) -> t.SequenceOf[int]:
            """File descriptors inherited by the child process."""
            ...

        @property
        def stderr_file(self) -> t.Cli.TextPath | None:
            """Separate durable stderr destination for durable output."""
            ...

        @property
        def isolation(self) -> FlextCliModelsProcess.ProcessReadOnlyIsolation | None:
            """Qualified immutable native confinement inputs."""
            ...


__all__: list[str] = ["FlextCliProtocolsProcess"]
