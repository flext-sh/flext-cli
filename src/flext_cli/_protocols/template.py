# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/template
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsTemplate:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class TemplateRenderOptions(Protocol):
        """Structural data contract projected from the owning model."""

        strip_suffix: str
        overwrite: bool

    @runtime_checkable
    class TemplateRenderEntry(Protocol):
        """Structural data contract projected from the owning model."""

        relpath_template: Path
        output_relpath: Path
        when: bool
        overwrite: bool

    @runtime_checkable
    class TemplateRenderReport(Protocol):
        """Structural data contract projected from the owning model."""

        created: tuple[Path, ...]
        skipped: tuple[Path, ...]
        failed: tuple[tuple[Path, str], ...]

    @runtime_checkable
    class AuthenticatedTemplateRender(Protocol):
        """Structural data contract projected from the owning model."""

        rendered: str
        source_states: tuple[p.Cli.AtomicFileState, ...]


__all__: list[str] = [
    "FlextCliProtocolsTemplate",
]
