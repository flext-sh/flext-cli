# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/markdown
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import p


class FlextCliProtocolsMarkdown:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class MarkdownFence(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def info(self) -> str:
            """Raw fence info string."""
            ...

        @property
        def language(self) -> str:
            """Lower-cased first token of the info string."""
            ...

        @property
        def code(self) -> str:
            """Fence body, verbatim."""
            ...

        @property
        def opening_line(self) -> int:
            """Source line of the opening fence."""
            ...

        @property
        def closing_line(self) -> int:
            """Last source line the block occupies."""
            ...

        @property
        def nested(self) -> bool:
            """Whether the fence sits inside a list or quote."""
            ...

    @runtime_checkable
    class MarkdownLink(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def target(self) -> str:
            """Destination, verbatim."""
            ...

        @property
        def line(self) -> int:
            """Source line of the link."""
            ...

        @property
        def image(self) -> bool:
            """Whether the token is an image."""
            ...

    @runtime_checkable
    class MarkdownHeading(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def level(self) -> int:
            """Heading depth."""
            ...

        @property
        def text(self) -> str:
            """Plain heading text."""
            ...

        @property
        def line(self) -> int:
            """Source line of the heading."""
            ...

    @runtime_checkable
    class MarkdownCodeSpan(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> str:
            """Code span content."""
            ...

        @property
        def prefix(self) -> str:
            """Rendered prose preceding the span on its line."""
            ...

        @property
        def line(self) -> int:
            """Source line of the span."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsMarkdown",
]
