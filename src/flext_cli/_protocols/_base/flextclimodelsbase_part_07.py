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

from flext_cli import t

if TYPE_CHECKING:
    from flext_core import p

    from flext_cli._constants import FlextCliConstantsEnums
    from flext_cli._typings import FlextCliTypesDomain


class FlextCliProtocolsBaseFlextclimodelsbasePart07:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ServiceOptions(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def structlog_options(self) -> p.StructlogOptions | None:
            """Optional native Core logging composition for this application."""
            ...

    @runtime_checkable
    class TypedExtract(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def type_kind(self) -> FlextCliTypesDomain.TypeKind:
            """Requested type."""
            ...

        @property
        def value(self) -> t.JsonValue | None:
            """Value to extract and coerce."""
            ...

        @property
        def default(self) -> t.JsonValue | None:
            """Fallback value when extraction fails."""
            ...

    @runtime_checkable
    class JsonWriteOptions(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        indent: int
        sort_keys: bool
        ensure_ascii: bool

    @runtime_checkable
    class TableRenderRequest(FlextProtocols.Model, Protocol):
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
    class DataReportRequest(FlextProtocols.Model, Protocol):
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
        def table_format(self) -> FlextCliConstantsEnums.TabularFormat:
            """Table rendering format for the data report."""
            ...

        @property
        def show_header(self) -> bool:
            """Whether to render the header row."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart07",
]
