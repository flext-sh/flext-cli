"""Read-only launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_02 import (
        FlextCliProtocolsBasePart02,
    )
    from flext_core import t


class FlextCliProtocolsProcess:
    """Structural process input declarations exposed through ``p.Cli``."""

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


__all__: list[str] = ["FlextCliProtocolsProcess"]
