"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, Protocol, Self, override, runtime_checkable

from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_01 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart01,
)
from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._settings import FlextCliSettings


class FlextCliProtocolsBase(FlextCliProtocolsBasePart01):
    """Implementation part for FlextCliProtocolsBase."""

    @runtime_checkable
    class Settings(p.Settings, Protocol):
        """Protocol for CLI runtime settings consumed by the public services."""

        # NOTE (multi-agent): ``Cli`` is the CONCRETE branch class, not the
        # structural ``CliSettings`` protocol (kept in part_01 for DI).
        # Root cause of the historical pyrefly failures: (1) as a plain
        # read-write attribute the member is invariant — any distinct branch
        # type fails; ``Final`` keeps it read-only/covariant while preserving
        # the domain-mandated ``Cli`` name (a ``@property`` would trip ruff
        # N802); (2) pyrefly cannot reconcile ANY pydantic BaseModel with
        # ``p.Model`` (``model_fields`` metaclass descriptor mismatch, proven
        # against instance/ClassVar/property forms), so the protocol branch
        # can never be satisfied on this hot path. The concrete type matches
        # exactly, flows into ``t.SettingsOverride`` via the ``BaseModel``
        # leaf (clone/update_global call sites in params.py/cli_part_02), and
        # is imported under TYPE_CHECKING per FLEXT rule 7. The settings
        # family is concrete-rooted (fetch_global/clone are FlextSettings
        # classmethods), so no implementation flexibility is lost.
        Cli: Final[FlextCliSettings.CliSettings]
        """Namespaced CLI settings branch (read-only contract)."""

        @property
        def debug(self) -> bool:
            """Check if debug mode is enabled."""
            ...

        @property
        def trace(self) -> bool:
            """Check if trace mode is enabled."""
            ...

        @override
        def model_dump(
            self,
            *,
            mode: str = "python",
            exclude_none: bool = False,
        ) -> t.JsonMapping:
            """Dump the settings model into a JSON-compatible mapping."""
            ...

        @override
        def clone(self, **overrides: t.SettingsOverride | None) -> Self:
            """Return a cloned settings instance with overrides applied."""
            ...

        @classmethod
        @override
        def fetch_global(
            cls,
            *,
            overrides: t.ScalarMapping | None = None,
        ) -> Self:
            """Return the process-wide singleton settings instance."""
            ...

        @classmethod
        @override
        def update_global(cls, **overrides: t.SettingsOverride | None) -> Self:
            """Replace the singleton via Pydantic-2 ``model_copy(update=…)``."""
            ...

        @classmethod
        def reset_for_testing(cls) -> None:
            """Reset the process-wide singleton (test isolation only)."""
            ...

    @runtime_checkable
    class SettingsType(p.SettingsType, Protocol):
        """Concrete CLI settings classes with singleton/test hooks."""

        @classmethod
        @override
        def fetch_global(
            cls,
            *,
            overrides: t.ScalarMapping | None = None,
        ) -> FlextCliProtocolsBase.Settings:
            """Return the process-wide singleton settings instance."""
            ...

        @classmethod
        def reset_for_testing(cls) -> None:
            """Reset the process-wide singleton (test isolation only)."""
            ...

    @runtime_checkable
    class CommandOutput(Protocol):
        """Minimal external command execution output contract."""

        @property
        def duration(self) -> float:
            """Return the command duration in seconds."""
            ...

        @property
        def exit_code(self) -> int:
            """Return the command exit code."""
            ...

        @property
        def stderr(self) -> str:
            """Return the command standard error."""
            ...

        @property
        def stdout(self) -> str:
            """Return the command standard output."""
            ...


__all__: list[str] = ["FlextCliProtocolsBase"]
