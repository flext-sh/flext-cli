# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/pptx_presentation
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsPptxPresentation:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class PptxSlidePlan(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def title(self) -> str:
            """Slide title."""
            ...

    @runtime_checkable
    class PptxPresentationPlan(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def slides(self) -> tuple[FlextCliProtocolsPptxPresentation.PptxSlidePlan, ...]:
            """Presentation slides."""
            ...

        @property
        def core_properties(self) -> t.JsonMapping:
            """Core document properties."""
            ...

    @runtime_checkable
    class PptxRenderRequest(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def template(self) -> bytes | None:
            """Formatting template bytes."""
            ...

        @property
        def plan(self) -> FlextCliProtocolsPptxPresentation.PptxPresentationPlan:
            """Validated presentation plan."""
            ...

    @runtime_checkable
    class PptxRenderResult(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes:
            """Rendered presentation bytes."""
            ...

        @property
        def plan(self) -> FlextCliProtocolsPptxPresentation.PptxPresentationPlan:
            """Exact source plan."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsPptxPresentation",
]
