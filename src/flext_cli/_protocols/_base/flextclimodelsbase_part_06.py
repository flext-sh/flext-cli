# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_06
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart01
    from flext_cli._typings import FlextCliTypesBase


class FlextCliProtocolsBaseFlextclimodelsbasePart06:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class CliParamsConfig(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def verbose(self) -> bool | None:
            """Enable verbose output."""
            ...

        @property
        def quiet(self) -> bool | None:
            """Suppress non-essential output."""
            ...

        @property
        def debug(self) -> bool | None:
            """Structural member projected from the owning model."""
            ...

        @property
        def trace(self) -> bool | None:
            """Structural member projected from the owning model."""
            ...

        @property
        def log_level(self) -> str | None:
            """Structural member projected from the owning model."""
            ...

        @property
        def log_format(self) -> str | None:
            """Log format (compact, detailed, full)."""
            ...

        @property
        def output_format(self) -> str | None:
            """Output format (table, json, yaml, csv)."""
            ...

        @property
        def no_color(self) -> bool | None:
            """Disable colored output."""
            ...

        @property
        def params(self) -> t.JsonMapping:
            """Parameters mapping - required by CliParamsConfig."""
            ...

    @runtime_checkable
    class OptionMetadata(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def help(self) -> str:
            """Option help text."""
            ...

        @property
        def short(self) -> str:
            """Single-letter short flag without leading dash."""
            ...

        @property
        def default(self) -> FlextCliTypesBase.CliValue | None:
            """Option default value when explicitly provided."""
            ...

        @property
        def field_name_override(self) -> str | None:
            """Override for the CLI-facing option name."""
            ...

    @runtime_checkable
    class OptionSpec(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def declarations(self) -> Sequence[str]:
            """Ordered long and short option declarations."""
            ...

        @property
        def help_text(self) -> str:
            """Human-readable option help."""
            ...

        @property
        def default(self) -> FlextCliTypesBase.CliValue | None:
            """Validated optional default value."""
            ...

        @property
        def required(self) -> bool:
            """Require an explicit option value."""
            ...

    @runtime_checkable
    class InvocationResult(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def exit_code(self) -> int:
            """Process-compatible exit code."""
            ...

        @property
        def stdout(self) -> str:
            """Captured standard output."""
            ...

        @property
        def stderr(self) -> str:
            """Captured standard error."""
            ...

        @property
        def outcome(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessOutcome:
            """Causal completion state for the invocation."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart06",
]
