"""FlextCliConstantsMarkdown - Markdown parser dialect constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum, unique
from typing import ClassVar


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
    MARKDOWN_INLINE_CORE_RULE: ClassVar[str] = "inline"
    """markdown-it core stage that parses inline content; fences never need it."""
    "CommonMark core shared by MkDocs and pytest-markdown-docs."
    MARKDOWN_PARSER_RULES: ClassVar[Sequence[str]] = ("table",)
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
    MARKDOWN_FENCE_MARKS: ClassVar[Sequence[str]] = ("```", "~~~")
    "Opening sequences of CommonMark code fences."
    MARKDOWN_CONTAINER_CHARS: ClassVar[str] = " \t>"
    "Characters that form list-indentation and block-quote container prefixes."
    MARKDOWN_WRAP_DEFAULT_WIDTH: ClassVar[int] = 80
    "Prose width used when a caller does not declare one."
    MARKDOWN_WRAP_STRUCTURAL_PREFIXES: ClassVar[Sequence[str]] = (
        "#",
        "|",
        ":::",
        "```",
        "<",
    )
    "Line openings that carry Markdown structure and are never reflowed."
    MARKDOWN_WRAP_BULLET_MARKERS: ClassVar[Sequence[str]] = ("- ", "* ", "+ ")
    "Unordered list markers whose continuation lines align under the text."
    MARKDOWN_WRAP_QUOTE_MARKER: ClassVar[str] = "> "
    "Block-quote marker repeated on every continuation line."


__all__: Sequence[str] = ("FlextCliConstantsMarkdown",)
