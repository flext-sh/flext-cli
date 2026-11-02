# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/pptx_presentation
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsPptxPresentation:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class PptxSlidePlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def title(self) -> str: ...

    @runtime_checkable
    class PptxPresentationPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def slides(self) -> tuple[p.Cli.PptxSlidePlan, ...]: ...
        @property
        def core_properties(self) -> t.JsonMapping: ...

    @runtime_checkable
    class PptxRenderRequest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def template(self) -> bytes | None: ...
        @property
        def plan(self) -> p.Cli.PptxPresentationPlan: ...

    @runtime_checkable
    class PptxRenderResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> bytes: ...
        @property
        def plan(self) -> p.Cli.PptxPresentationPlan: ...


__all__: list[str] = [
    "FlextCliProtocolsPptxPresentation",
]
