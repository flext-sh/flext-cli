"""Flext-cli config models (m facade).

Typed, frozen shapes for the ``config/*.yaml`` business-rule SSOT (§2.0b).
Each model owns one declared top-level YAML namespace and is validated at
``FlextCliConfig.fetch_global`` construction. The config facade
``flext_cli.config`` composes them as typed namespace fields.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, get_args

from flext_core import m, u

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
"""Closed vocabulary of complete symbolic syscalls the native policy may deny.

Names such as ``listen`` are syscall identifiers, not CQRS action prefixes.
"""


class FlextCliModelsConfig:
    """Native owner of the typed ``config/*.yaml`` models for flext-cli."""

    class Cli(m.FrozenModel):
        """CLI identity metadata from ``config/cli.yaml``."""

        name: str = m.Field(
            min_length=1, description="Configured CLI application name."
        )
        version: str = m.Field(
            min_length=1, description="Configured CLI application version."
        )

    class ProcessIsolation(m.FrozenModel):
        """Immutable syscall obligations of native read-only reference imports."""

        compiler_resource_parts: tuple[str, ...] = m.Field(
            min_length=1,
            description=(
                "Exact relative parts elected in the declared distribution RECORD"
            ),
        )
        denied_syscalls: tuple[DeniedSyscallName, ...] = m.Field(
            description="Symbolic native network and io_uring denials",
        )

        @m.field_validator(
            "compiler_resource_parts",
            "denied_syscalls",
            mode="before",
        )
        @classmethod
        def _coerce_yaml_sequences(
            cls, value: t.JsonValue | t.StrTuple
        ) -> t.JsonValue | tuple[t.JsonValue, ...]:
            """Coerce declared YAML sequences into the strict tuple form.

            Args:
                value: The raw declared value.

            Returns:
                The coerced tuple.

            """
            return tuple(value) if isinstance(value, list) else value

        @m.field_validator("compiler_resource_parts")
        @classmethod
        def _validate_resource_parts(cls, value: tuple[str, ...]) -> tuple[str, ...]:
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
                or any(character in part for character in "/\\\0")
                for part in value
            ):
                msg = (
                    "native compiler resource parts must be lexical relative components"
                )
                raise ValueError(msg)
            return value

        @m.field_validator("denied_syscalls")
        @classmethod
        def _validate_policy_floor(
            cls, value: tuple[DeniedSyscallName, ...]
        ) -> tuple[DeniedSyscallName, ...]:
            """Require every native syscall obligation exactly once.

            Returns:
                The declared order of the complete native policy.

            Raises:
                ValueError: If a required syscall is missing or duplicated.

            """
            required = u.type_adapter(tuple[DeniedSyscallName, ...]).validate_python(
                get_args(DeniedSyscallName.__value__), strict=True
            )
            if len(value) != len(required) or set(value) != set(required):
                msg = (
                    "denied_syscalls must contain every native syscall obligation "
                    "exactly once"
                )
                raise ValueError(msg)
            return value


__all__: tuple[str, ...] = ("FlextCliModelsConfig",)
