"""FlextCliConstantsMarkdown - Markdown parser dialect constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from flext_core import t


class FlextCliConstantsMarkdown:
    """SSOT for the Markdown dialect parsed by ``u.Cli.markdown_*``."""

    @unique
    class MarkdownTokenType(StrEnum):
        """markdown-it-py token types consumed by ``u.Cli.markdown_*``."""

        FENCE = "fence"
        INLINE = "inline"
        LINK_OPEN = "link_open"
        IMAGE = "image"
        CODE_INLINE = "code_inline"
        HEADING_OPEN = "heading_open"
        SOFTBREAK = "softbreak"
        HARDBREAK = "hardbreak"

    MARKDOWN_PARSER_PRESET: ClassVar[str] = "commonmark"
    "CommonMark core shared by MkDocs and pytest-markdown-docs."
    MARKDOWN_PARSER_RULES: ClassVar[t.StrSequence] = ("table",)
    "GFM table rule enabled to match the generated MkDocs ``tables`` extension."
    MARKDOWN_LINE_BREAK_TOKENS: ClassVar[frozenset[str]] = frozenset({
        MarkdownTokenType.SOFTBREAK,
        MarkdownTokenType.HARDBREAK,
    })
    "Inline tokens that advance the source line inside one block."
    MARKDOWN_AUTOLINK_MARKUP: ClassVar[str] = "autolink"
    "Markup of ``<scheme:...>`` autolinks, which carry no authored destination."
    MARKDOWN_LINKIFY_MARKUP: ClassVar[str] = "linkify"
    "Markup of bare URLs promoted to links by the linkify rule."
    MARKDOWN_FENCE_MARKS: ClassVar[t.StrSequence] = ("```", "~~~")
    "Opening sequences of CommonMark code fences."
    MARKDOWN_CONTAINER_CHARS: ClassVar[str] = " \t>"
    "Characters that form list-indentation and block-quote container prefixes."


__all__: t.StrSequence = ("FlextCliConstantsMarkdown",)
