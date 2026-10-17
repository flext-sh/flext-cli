"""Flext-cli config models (m facade).

Typed, frozen shapes for the ``config/*.yaml`` business-rule SSOT (§2.0b).
Each model owns one declared top-level YAML namespace and is validated at
``FlextCliConfig.fetch_global`` construction. The config facade
``flext_cli.config`` composes them as typed namespace fields.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from flext_core import m

if TYPE_CHECKING:
    from flext_core import t

type DeniedSyscallName = Literal[
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
]
"""Closed vocabulary of symbolic syscalls the native policy may deny."""


class FlextCliConfigModels:
    """Native owner of the typed ``config/*.yaml`` models for flext-cli."""

    class Cli(m.FrozenModel):
        """CLI identity metadata from ``config/cli.yaml``."""

        name: str = m.Field(description="Configured CLI application name.")
        version: str = m.Field(description="Configured CLI application version.")

    class ProcessIsolation(m.FrozenModel):
        """Immutable syscall obligations of native read-only reference imports."""

        compiler_resource_parts: tuple[str, ...] = m.Field(
            default=(),
            description=(
                "Exact relative parts elected in the declared distribution RECORD"
            ),
        )
        denied_syscalls: tuple[DeniedSyscallName, ...] = m.Field(
            default=(),
            description="Symbolic native network and io_uring denials",
        )

        @m.field_validator(
            "compiler_resource_parts",
            "denied_syscalls",
            mode="before",
        )
        @classmethod
        def _coerce_yaml_sequences(cls, value: object) -> object:
            """Coerce declared YAML sequences into the strict tuple form.

            Args:
                value: The raw declared value.

            Returns:
                The coerced tuple.

            """
            return tuple(value) if isinstance(value, list) else value

        @m.field_validator("compiler_resource_parts")
        @classmethod
        def _validate_resource_parts(
            cls,
            value: tuple[str, ...],
        ) -> tuple[str, ...]:
            """Reject any part escaping one lexical relative component.

            Args:
                value: The declared relative parts.

            Returns:
                The validated parts.

            Raises:
                ValueError: If any part is empty, dotted, or path-carrying.

            """
            if any(
                not part
                or part in {".", ".."}
                or "/" in part
                or "\\" in part
                or "\0" in part
                for part in value
            ):
                msg = (
                    "native compiler resource parts must be lexical relative components"
                )
                raise ValueError(msg)
            return value


__all__: t.VariadicTuple[str] = ("FlextCliConfigModels",)
