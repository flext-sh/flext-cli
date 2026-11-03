# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_xlsx/xlsx_style_catalog
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._xlsx import FlextCliProtocolsXlsxXlsxStyles


class FlextCliProtocolsXlsxXlsxStyleCatalog:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class XlsxStyleMapEntry(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source_style_id(self) -> int:
            """Source workbook style identifier."""
            ...

        @property
        def style_name(self) -> str:
            """Generated named style key."""
            ...

    @runtime_checkable
    class XlsxSourceVisualStyle(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source_style_id(self) -> int:
            """Source workbook style identifier."""
            ...

        @property
        def visual(self) -> FlextCliProtocolsXlsxXlsxStyles.XlsxVisualStyleSpec:
            """Protection-free source visual signature."""
            ...

    @runtime_checkable
    class XlsxStyleCatalog(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def style_map(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxStyleCatalog.XlsxStyleMapEntry, ...]:
            """Source style assignments."""
            ...

        @property
        def styles(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxStyles.XlsxNamedStyleSpec, ...]:
            """Unique visual styles."""
            ...

    @runtime_checkable
    class XlsxStyleCatalogRequest(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Source workbook bytes."""
            ...

        @property
        def style_name_prefix(self) -> str:
            """Generated style-name prefix."""
            ...

    @runtime_checkable
    class XlsxStyleTemplateRequest(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def source(self) -> bytes:
            """Source workbook bytes."""
            ...

        @property
        def style_name_prefix(self) -> str:
            """Generated style-name prefix."""
            ...

    @runtime_checkable
    class XlsxStyleTemplateResult(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes:
            """Format-only workbook bytes."""
            ...

        @property
        def style_map(
            self,
        ) -> tuple[FlextCliProtocolsXlsxXlsxStyleCatalog.XlsxStyleMapEntry, ...]:
            """Source style assignments."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsXlsxXlsxStyleCatalog",
]
