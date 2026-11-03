"""Config-domain protocols part (composed into ``p.Cli`` via MRO).

Structural, field-level protocols for the validated config domains — never
model classes, never ``Any``/``object``. No runtime project imports; importable
by ``c``/``t``/``p``/``m``/``u`` without creating a cycle (foundation purity).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from typing import Literal


class FlextCliProtocolsConfig:
    """Config-domain protocol namespace (structural types; no project imports)."""

    @runtime_checkable
    class Cli(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Configured CLI application name."""
            ...

        @property
        def version(self) -> str:
            """Configured CLI application version."""
            ...

    @runtime_checkable
    class ProcessIsolation(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def compiler_resource_parts(self) -> tuple[str, ...]:
            """Exact relative parts elected in the declared distribution RECORD."""
            ...

        @property
        def denied_syscalls(
            self,
        ) -> tuple[
            Literal[
                "socket",
                "socketpair",
                "connect",
                "bind",
                "listen",
                "accept",
                "accept4",
                "sendto",
                "recvfrom",
                "sendmsg",
                "recvmsg",
                "sendmmsg",
                "recvmmsg",
                "io_uring_setup",
                "io_uring_enter",
                "io_uring_register",
            ],
            ...,
        ]:
            """Symbolic native network and io_uring denials."""
            ...


__all__: list[str] = ["FlextCliProtocolsConfig"]
