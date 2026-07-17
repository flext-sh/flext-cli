"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsBase:
    """Implementation part for FlextCliProtocolsBase."""

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
