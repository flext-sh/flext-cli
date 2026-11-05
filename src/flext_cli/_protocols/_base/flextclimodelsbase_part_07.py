# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_07
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_core import p

    from flext_cli import c, t


class FlextCliProtocolsBaseFlextclimodelsbasePart07:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ServiceOptions(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def structlog_options(self) -> p.StructlogOptions | None:
            """Optional native Core logging composition for this application."""
            ...

    @runtime_checkable
    class TypedExtract(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        type_kind: t.Cli.TypeKind
        value: t.JsonValue | None
        default: t.JsonValue | None

    @runtime_checkable
    class JsonWriteOptions(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        indent: int
        sort_keys: bool
        ensure_ascii: bool

    @runtime_checkable
    class TableRenderRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def columns(self) -> Sequence[str]:
            """Ordered table column labels."""
            ...

        @property
        def rows(self) -> Sequence[Sequence[str]]:
            """Ordered table row values."""
            ...

        @property
        def title(self) -> str:
            """Optional table title."""
            ...

    @runtime_checkable
    class DataReportRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def columns(self) -> Sequence[str]:
            """Ordered report column labels."""
            ...

        @property
        def rows(self) -> Sequence[Sequence[str]]:
            """Ordered report row values."""
            ...

        @property
        def title(self) -> str:
            """Optional report title."""
            ...

        @property
        def message(self) -> str:
            """Trailing verdict line emitted after the table."""
            ...

        @property
        def table_format(self) -> c.Cli.TabularFormat:
            """Table rendering format for the data report."""
            ...

        @property
        def show_header(self) -> bool:
            """Whether to render the header row."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart07",
]
