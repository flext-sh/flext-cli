# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_style_catalog
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsXlsxXlsxStyleCatalog:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class XlsxStyleMapEntry(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source_style_id(self) -> int: ...
        @property
        def style_name(self) -> str: ...

    @runtime_checkable
    class XlsxSourceVisualStyle(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source_style_id(self) -> int: ...
        @property
        def visual(self) -> p.Cli.XlsxVisualStyleSpec: ...

    @runtime_checkable
    class XlsxStyleCatalog(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def style_map(self) -> tuple[p.Cli.XlsxStyleMapEntry, ...]: ...
        @property
        def styles(self) -> tuple[p.Cli.XlsxNamedStyleSpec, ...]: ...

    @runtime_checkable
    class XlsxStyleCatalogRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...
        @property
        def style_name_prefix(self) -> str: ...

    @runtime_checkable
    class XlsxStyleTemplateRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes: ...
        @property
        def style_name_prefix(self) -> str: ...

    @runtime_checkable
    class XlsxStyleTemplateResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes: ...
        @property
        def style_map(self) -> tuple[p.Cli.XlsxStyleMapEntry, ...]: ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStyleCatalog",
]
