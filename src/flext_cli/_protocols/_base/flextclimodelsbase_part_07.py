# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_07
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_core import p

    from flext_cli import c, p, t
    from flext_cli.protocols import p


class FlextCliProtocolsBaseFlextclimodelsbasePart07:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class ServiceOptions(Protocol):
        """Structural data contract projected from the owning model."""

        structlog_options: p.StructlogOptions | None

    @runtime_checkable
    class TypedExtract(Protocol):
        """Structural data contract projected from the owning model."""

        type_kind: t.Cli.TypeKind
        value: t.JsonValue | None
        default: t.JsonValue | None

    @runtime_checkable
    class JsonWriteOptions(Protocol):
        """Structural data contract projected from the owning model."""

        indent: int
        sort_keys: bool
        ensure_ascii: bool

    @runtime_checkable
    class TableRenderRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def columns(self) -> Sequence[str]: ...
        @property
        def rows(self) -> Sequence[Sequence[str]]: ...
        @property
        def title(self) -> str: ...

    @runtime_checkable
    class DataReportRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def columns(self) -> Sequence[str]: ...
        @property
        def rows(self) -> Sequence[Sequence[str]]: ...
        @property
        def title(self) -> str: ...
        @property
        def message(self) -> str: ...
        @property
        def table_format(self) -> c.Cli.TabularFormat: ...
        @property
        def show_header(self) -> bool: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart07",
]
