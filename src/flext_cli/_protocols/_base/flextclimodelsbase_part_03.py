# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_03
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart02

if TYPE_CHECKING:
    from flext_cli import c, t
    from flext_cli._protocols import FlextCliProtocolsDomain


class FlextCliProtocolsBaseFlextclimodelsbasePart03:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicDirectoryState(
        FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicPhysicalIdentity, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def exists(self) -> bool:
            """Whether the directory exists."""
            ...

    @runtime_checkable
    class CommandEntryModel(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        name: t.NonEmptyStr
        handler: t.Cli.JsonCommandFn

    @runtime_checkable
    class EmptyRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

    @runtime_checkable
    class CommandMetadata(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> t.NonEmptyStr:
            """Command name."""
            ...

        @property
        def help_text(self) -> str:
            """User-facing help text."""
            ...

    @runtime_checkable
    class ResultCommandRoute(CommandMetadata, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def model_cls(self) -> t.ModelClass[t.Cli.ModelLike]:
            """Pydantic input model class."""
            ...

        @property
        def handler(self) -> FlextCliProtocolsDomain.ResultRouteHandler:
            """Command handler returning r[...]."""
            ...

        @property
        def success_message(self) -> str | None:
            """Static success message."""
            ...

        @property
        def success_formatter(self) -> t.Cli.SuccessMessageFormatter | None:
            """Dynamic success formatter."""
            ...

        @property
        def success_type(self) -> c.Cli.MessageTypes:
            """CLI output style on success."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart03",
]
