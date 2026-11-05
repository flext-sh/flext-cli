# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_03
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._constants import FlextCliConstantsEnums
    from flext_cli._protocols import FlextCliProtocolsDomain
    from flext_cli._typings import FlextCliTypesDomain


class FlextCliProtocolsBaseFlextclimodelsbasePart03:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicDirectoryState(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Absolute directory path."""
            ...

        @property
        def exists(self) -> bool:
            """Whether the directory exists."""
            ...

        @property
        def parent_device(self) -> int | None:
            """Physical parent device, or None when the chain is absent."""
            ...

        @property
        def parent_inode(self) -> int | None:
            """Physical parent inode, or None when the chain is absent."""
            ...

        @property
        def mode(self) -> int | None:
            """Permission bits."""
            ...

        @property
        def device(self) -> int | None:
            """Physical device."""
            ...

        @property
        def inode(self) -> int | None:
            """Physical inode."""
            ...

        @property
        def link_count(self) -> int | None:
            """Exact link count."""
            ...

        @property
        def file_attributes(self) -> int | None:
            """Host attributes."""
            ...

        @property
        def reparse_tag(self) -> int | None:
            """Host reparse tag."""
            ...

    @runtime_checkable
    class CommandEntryModel(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        name: t.NonEmptyStr

        @property
        def handler(self) -> FlextCliTypesDomain.JsonCommandFn:
            """Command handler callable."""
            ...

    @runtime_checkable
    class EmptyRequest(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

    @runtime_checkable
    class CommandMetadata(p.BaseModel, Protocol):
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
        def model_cls(self) -> t.ModelClass[FlextCliTypesDomain.ModelLike]:
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
        def success_formatter(
            self,
        ) -> FlextCliTypesDomain.SuccessMessageFormatter | None:
            """Dynamic success formatter."""
            ...

        @property
        def success_type(self) -> FlextCliConstantsEnums.MessageTypes:
            """CLI output style on success."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart03",
]
