"""Canonical launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

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


__all__: list[str] = ["FlextCliModelsProcess"]
