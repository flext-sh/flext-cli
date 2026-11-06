# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/template
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart02


class FlextCliProtocolsTemplate:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class TemplateRenderOptions(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        strip_suffix: str
        overwrite: bool

    @runtime_checkable
    class TemplateRenderEntry(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        relpath_template: Path
        output_relpath: Path
        when: bool
        overwrite: bool

    @runtime_checkable
    class TemplateRenderReport(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        created: tuple[Path, ...]
        skipped: tuple[Path, ...]
        failed: tuple[tuple[Path, str], ...]

    @runtime_checkable
    class AuthenticatedTemplateRender(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        rendered: str

        @property
        def source_states(
            self,
        ) -> tuple[FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState, ...]:
            """Ordered physical states of the template and its imports."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsTemplate",
]
