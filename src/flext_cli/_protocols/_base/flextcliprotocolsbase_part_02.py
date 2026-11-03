"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import IO, Protocol, runtime_checkable

from flext_core import p

from flext_cli._protocols._base import FlextCliProtocolsBasePart01


class FlextCliProtocolsBasePart02(FlextCliProtocolsBasePart01):
    """Implementation part for FlextCliProtocolsBasePart02."""

    @runtime_checkable
    class Settings(
        p.LoggingSettings,
        FlextCliProtocolsBasePart01.CliSettings,
        Protocol,
    ):
        """Protocol for CLI runtime settings consumed by the public services.

        NOTE (multi-agent): settings are flat ``cli_*`` scalars (§2.6); the
        nested ``Cli`` branch and its pyrefly ``Final`` workaround were
        removed with it. The flat field contract comes from
        ``CliSettings`` (part_01) via protocol composition.
        """

        @classmethod
        def reset_for_testing(cls) -> None:
            """Reset the process-wide singleton (test isolation only)."""
            ...

    # mro-zf1s: binary command consumers type against p, never the model owner.

    @runtime_checkable
    class ProcessHandle(Protocol):
        """Raw child handle owned by the single spawn engine.

        The engine owner returns exactly one native child through this
        contract; portable lifecycle utilities and the managed facade each
        consume the declared members they need and adapt their public
        contracts at their own boundaries.
        """

        @property
        def pid(self) -> int:
            """Operating-system process identifier."""
            ...

        @property
        def stdout(self) -> IO[bytes] | None:
            """Binary standard-output pipe when requested."""
            ...

        @property
        def stderr(self) -> IO[bytes] | None:
            """Binary standard-error pipe when requested separately."""
            ...

        @property
        def stdin(self) -> IO[bytes] | None:
            """Binary standard-input pipe when requested."""
            ...

        def communicate(
            self,
            input_data: bytes | None = None,
            /,
            timeout: float | None = None,
        ) -> tuple[bytes | None, bytes | None]:
            """Send binary input and drain pipes; inherited streams return None."""
            ...

        def kill(self) -> None:
            """Force termination of the root process."""
            ...

        def poll(self) -> int | None:
            """Return the root exit code when available."""
            ...

        def send_signal(self, sig: int) -> None:
            """Send one platform signal to the root process."""
            ...

        def wait(self) -> int:
            """Block until the root process is reaped and return its exit code."""
            ...


__all__: list[str] = ["FlextCliProtocolsBasePart02"]
