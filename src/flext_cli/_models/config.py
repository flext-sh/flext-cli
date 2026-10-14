"""Flext-cli config models (m facade; no project-specific imports).

Typed, frozen shapes for the ``config/*.yaml`` business-rule SSOT. This module
imports only the ``flext_core.m`` facade — the ``_config.py`` facade validates the
model-less YAML slices into these classes and exposes the ready objects under
``config.Cli``. Adding a new config domain = add a nested model here and a
validated field on ``Root`` (§2.0b reference: cosmos-main ``_models/config.py``).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_core import m


class FlextCliConfigModels:
    """Namespace of typed flext-cli config models (m facade)."""

    class Cli(m.BaseModel):
        """CLI identity metadata from ``config/cli.yaml``."""

        model_config = m.ConfigDict(frozen=True, extra="forbid")

        name: str
        version: str

    class ProcessIsolation(m.BaseModel):
        """Immutable syscall obligations of native read-only reference imports."""

        model_config = m.ConfigDict(frozen=True, extra="forbid")
        compiler_resource_parts: tuple[str, ...] = m.Field(
            min_length=1,
            description="Exact relative parts elected in the declared distribution RECORD",
        )
        denied_syscalls: tuple[
            Literal["socket"],
            Literal["socketpair"],
            Literal["connect"],
            Literal["bind"],
            Literal["listen"],
            Literal["accept"],
            Literal["accept4"],
            Literal["sendto"],
            Literal["recvfrom"],
            Literal["sendmsg"],
            Literal["recvmsg"],
            Literal["sendmmsg"],
            Literal["recvmmsg"],
            Literal["io_uring_setup"],
            Literal["io_uring_enter"],
            Literal["io_uring_register"],
        ] = m.Field(description="Required symbolic native network and io_uring denials")

        @m.field_validator("compiler_resource_parts")
        @classmethod
        def _validate_resource_parts(cls, value: tuple[str, ...]) -> tuple[str, ...]:
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

    class Root(m.BaseModel):
        """Root flext-cli runtime config validated from ``config/*.yaml``."""

        model_config = m.ConfigDict(frozen=True, extra="ignore")

        Cli: FlextCliConfigModels.Cli

        ProcessIsolation: FlextCliConfigModels.ProcessIsolation = m.Field(
            description="Native read-only reference import policy"
        )


__all__: list[str] = ["FlextCliConfigModels"]
