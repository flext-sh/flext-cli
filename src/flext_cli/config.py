"""Public configuration facade for Flext CLI.

FlextCliConfig — frozen, validated config singleton for flext-cli (§2.0b).

Every ``config/*.yaml`` file is auto-discovered and deep-merged at first
``fetch_global`` call (model-less, ``extra=allow`` at the FlextConfig base).
The flat YAML is then validated into the natively declared model shapes and
exposed as typed domain objects (``config.Cli.name`` / ``config.Cli.version``)
— never a model-less dict subscript (§2.2/§2.4).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal

from flext_core import FlextConfig, m

if TYPE_CHECKING:
    from flext_core import t


class FlextCliConfig(FlextConfig):
    """Cli config auto-loaded from ``config/*.yaml`` and validated via models."""

    # Anchored to the package dir so the YAML SSOT loads regardless of the
    # caller's CWD (library code must not depend on CWD).
    CONFIG_DIR: ClassVar[str] = str(Path(__file__).resolve().parent / "config")

    class Models:
        """Validated shapes of the ``config/*.yaml`` business-rule SSOT."""

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
                description=(
                    "Exact relative parts elected in the declared distribution RECORD"
                ),
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
            ] = m.Field(
                description="Required symbolic native network and io_uring denials",
            )

            @m.field_validator("compiler_resource_parts")
            @classmethod
            def _validate_resource_parts(
                cls,
                value: tuple[str, ...],
            ) -> tuple[str, ...]:
                if any(
                    not part
                    or part in {".", ".."}
                    or "/" in part
                    or "\\" in part
                    or "\0" in part
                    for part in value
                ):
                    msg = (
                        "native compiler resource parts must be lexical relative "
                        "components"
                    )
                    raise ValueError(msg)
                return value

        class Root(m.BaseModel):
            """Root flext-cli runtime config validated from ``config/*.yaml``."""

            model_config = m.ConfigDict(frozen=True, extra="ignore")

            Cli: Models.Cli

            ProcessIsolation: Models.ProcessIsolation = m.Field(
                description="Native read-only reference import policy",
            )

    @cached_property
    def Cli(self) -> FlextCliConfig.Models.Root.Cli:
        """Validated ``Cli`` config domain (name/version identity metadata)."""
        root = FlextCliConfig.Models.Root.model_validate(dict(self.model_extra or {}))
        return root.Cli

    @cached_property
    def ProcessIsolation(self) -> FlextCliConfig.Models.Root.ProcessIsolation:
        """Validated native read-only reference process policy."""
        root = FlextCliConfig.Models.Root.model_validate(dict(self.model_extra or {}))
        return root.ProcessIsolation


config: FlextCliConfig = FlextCliConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_cli import config``."""

__all__: t.VariadicTuple[str] = ("FlextCliConfig", "config")
