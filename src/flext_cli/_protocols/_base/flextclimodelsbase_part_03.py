# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_03
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import p

    from flext_cli import c, p, t
    from flext_cli.protocols import p


class FlextCliProtocolsBaseFlextclimodelsbasePart03:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class AtomicDirectoryState(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def exists(self) -> bool: ...
        @property
        def parent_device(self) -> int | None: ...
        @property
        def parent_inode(self) -> int | None: ...
        @property
        def mode(self) -> int | None: ...
        @property
        def device(self) -> int | None: ...
        @property
        def inode(self) -> int | None: ...
        @property
        def link_count(self) -> int | None: ...
        @property
        def file_attributes(self) -> int | None: ...
        @property
        def reparse_tag(self) -> int | None: ...

    @runtime_checkable
    class CommandEntryModel(Protocol):
        """Structural data contract projected from the owning model."""

        name: t.NonEmptyStr
        handler: t.Cli.JsonCommandFn

    @runtime_checkable
    class EmptyRequest(Protocol):
        """Structural data contract projected from the owning model."""

    @runtime_checkable
    class CommandMetadata(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> t.NonEmptyStr: ...
        @property
        def help_text(self) -> str: ...

    @runtime_checkable
    class ResultCommandRoute(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> t.NonEmptyStr: ...
        @property
        def help_text(self) -> str: ...
        @property
        def model_cls(self) -> t.ModelClass[t.Cli.ModelLike]: ...
        @property
        def handler(self) -> p.Cli.ResultRouteHandler: ...
        @property
        def success_message(self) -> str | None: ...
        @property
        def success_formatter(self) -> t.Cli.SuccessMessageFormatter | None: ...
        @property
        def success_type(self) -> c.Cli.MessageTypes: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart03",
]
