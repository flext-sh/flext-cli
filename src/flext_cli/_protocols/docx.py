"""Writable python-docx contracts retained until facade withdrawal is generated.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph


class FlextCliProtocolsDocx:
    """Structural contracts currently published by the protocol facade."""

    class DocxParagraphContainer(Protocol):
        """Paragraph creation consumed by the existing document renderer."""

        def add_paragraph(
            self, text: str = "", style: str | None = None
        ) -> Paragraph:
            """Create a paragraph using the external library contract."""
            ...

    class DocxFontVariants(Protocol):
        """Writable tri-state character properties."""

        @property
        def superscript(self) -> bool | None:
            """Read superscript state."""
            ...

        @superscript.setter
        def superscript(self, value: bool | None) -> None:
            """Write superscript state."""
            ...

        @property
        def subscript(self) -> bool | None:
            """Read subscript state."""
            ...

        @subscript.setter
        def subscript(self, value: bool | None) -> None:
            """Write subscript state."""
            ...

        @property
        def all_caps(self) -> bool | None:
            """Read all-caps state."""
            ...

        @all_caps.setter
        def all_caps(self, value: bool | None) -> None:
            """Write all-caps state."""
            ...

        @property
        def small_caps(self) -> bool | None:
            """Read small-caps state."""
            ...

        @small_caps.setter
        def small_caps(self, value: bool | None) -> None:
            """Write small-caps state."""
            ...

    class DocxParagraphPagination(Protocol):
        """Writable tri-state pagination properties."""

        @property
        def keep_together(self) -> bool | None:
            """Read keep-together state."""
            ...

        @keep_together.setter
        def keep_together(self, value: bool | None) -> None:
            """Write keep-together state."""
            ...

        @property
        def keep_with_next(self) -> bool | None:
            """Read keep-with-next state."""
            ...

        @keep_with_next.setter
        def keep_with_next(self, value: bool | None) -> None:
            """Write keep-with-next state."""
            ...

        @property
        def page_break_before(self) -> bool | None:
            """Read page-break-before state."""
            ...

        @page_break_before.setter
        def page_break_before(self, value: bool | None) -> None:
            """Write page-break-before state."""
            ...

        @property
        def widow_control(self) -> bool | None:
            """Read widow-control state."""
            ...

        @widow_control.setter
        def widow_control(self, value: bool | None) -> None:
            """Write widow-control state."""
            ...


__all__: list[str] = ["FlextCliProtocolsDocx"]
