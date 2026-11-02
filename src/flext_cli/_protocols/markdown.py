# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/markdown
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsMarkdown:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class MarkdownFence(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def info(self) -> str: ...
        @property
        def language(self) -> str: ...
        @property
        def code(self) -> str: ...
        @property
        def opening_line(self) -> int: ...
        @property
        def closing_line(self) -> int: ...
        @property
        def nested(self) -> bool: ...

    @runtime_checkable
    class MarkdownLink(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def target(self) -> str: ...
        @property
        def line(self) -> int: ...
        @property
        def image(self) -> bool: ...

    @runtime_checkable
    class MarkdownHeading(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def level(self) -> int: ...
        @property
        def text(self) -> str: ...
        @property
        def line(self) -> int: ...

    @runtime_checkable
    class MarkdownCodeSpan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def content(self) -> str: ...
        @property
        def prefix(self) -> str: ...
        @property
        def line(self) -> int: ...


__all__: list[str] = [
    "FlextCliProtocolsMarkdown",
]
