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
    class TemplateRenderOptions(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        strip_suffix: str
        overwrite: bool

    @runtime_checkable
    class TemplateRenderEntry(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def relpath_template(self) -> Path:
            """Template path relative to templates_root (ends with .j2)."""
            ...

        @property
        def output_relpath(self) -> Path:
            """Structural member projected from the owning model.

            Output path relative to output_root; a trailing template suffix is
            stripped by the engine. Path tokens are resolved by the caller before
            invocation.
            """
            ...

        when: bool
        overwrite: bool

    @runtime_checkable
    class TemplateRenderReport(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def created(self) -> tuple[Path, ...]:
            """Destination paths written."""
            ...

        @property
        def skipped(self) -> tuple[Path, ...]:
            """Destinations skipped (exists or disabled)."""
            ...

        @property
        def failed(self) -> tuple[tuple[Path, str], ...]:
            """(destination, error) pairs that failed to render."""
            ...

    @runtime_checkable
    class AuthenticatedTemplateRender(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def rendered(self) -> str:
            """Text rendered from authenticated template bytes."""
            ...

        @property
        def source_states(
            self,
        ) -> tuple[FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState, ...]:
            """Ordered physical states of the template and its imports."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsTemplate",
]
