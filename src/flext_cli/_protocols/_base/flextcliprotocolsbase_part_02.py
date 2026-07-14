"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli._protocols._base.flextcliprotocolsbase_part_01 import (
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
            """Command exit status."""
            ...

        @property
        def stderr(self) -> str:
            """Command standard-error text."""
            ...

        @property
        def stdout(self) -> str:
            """Command standard-output text."""
            ...

    # mro-wkii.17.26 (codex): expose byte-exact process output structurally.
    @runtime_checkable
    class CommandBytesOutput(Protocol):
        """Minimal byte-exact external command execution output contract."""

        @property
        def duration(self) -> float:
            """Command duration in seconds."""
            ...

        @property
        def exit_code(self) -> int:
            """Command exit status."""
            ...

        @property
        def stderr(self) -> bytes:
            """Byte-exact command standard error."""
            ...

        @property
        def stdout(self) -> bytes:
            """Byte-exact command standard output."""
            ...


__all__: list[str] = ["FlextCliProtocolsBase"]
