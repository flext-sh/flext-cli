# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_06
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsBaseFlextclimodelsbasePart06:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class CliParamsConfig(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def verbose(self) -> bool | None: ...
        @property
        def quiet(self) -> bool | None: ...
        @property
        def debug(self) -> bool | None: ...
        @property
        def trace(self) -> bool | None: ...
        @property
        def log_level(self) -> str | None: ...
        @property
        def log_format(self) -> str | None: ...
        @property
        def output_format(self) -> str | None: ...
        @property
        def no_color(self) -> bool | None: ...

    @runtime_checkable
    class OptionMetadata(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def help(self) -> str: ...
        @property
        def short(self) -> str: ...
        @property
        def default(self) -> t.Cli.CliValue | None: ...
        @property
        def field_name_override(self) -> str | None: ...

    @runtime_checkable
    class OptionSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def declarations(self) -> Sequence[str]: ...
        @property
        def help_text(self) -> str: ...
        @property
        def default(self) -> t.Cli.CliValue | None: ...
        @property
        def required(self) -> bool: ...

    @runtime_checkable
    class InvocationResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def exit_code(self) -> int: ...
        @property
        def stdout(self) -> str: ...
        @property
        def stderr(self) -> str: ...
        @property
        def outcome(self) -> p.Cli.ProcessOutcome: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart06",
]
