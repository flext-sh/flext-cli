"""Shared markdown-it-py parsers behind the ``u.Cli.markdown_*`` queries.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import cache
from typing import TYPE_CHECKING, override

from markdown_it import MarkdownIt

from flext_cli import c

if TYPE_CHECKING:
    from markdown_it.token import Token


class FlextCliUtilitiesMarkdownParsing:
    """Own the verbatim parser dialect and the inline token walk."""

    class _VerbatimMarkdownIt(MarkdownIt):
        """Parser that keeps link destinations exactly as authored."""

        @override
        def normalizeLink(self, url: str) -> str:
            return url

        @override
        def validateLink(self, url: str) -> bool:
            return True

    @staticmethod
    @cache
    def _markdown_parser() -> MarkdownIt:
        """Return the shared parser aligned with the generated MkDocs dialect.

        Returns:
            The cached ``MarkdownIt`` instance.

        """
        parser = FlextCliUtilitiesMarkdownParsing._VerbatimMarkdownIt(
            c.Cli.MARKDOWN_PARSER_PRESET,
        )
        return parser.enable(list(c.Cli.MARKDOWN_PARSER_RULES))

    @staticmethod
    def _markdown_tokens(text: str) -> Sequence[Token]:
        """Parse one Markdown document into its block token stream.

        Returns:
            The parsed block tokens.

        """
        return FlextCliUtilitiesMarkdownParsing._markdown_parser().parse(text)

    @staticmethod
    @cache
    def _markdown_block_parser() -> MarkdownIt:
        """Return the shared parser restricted to the block structure.

        Fences are block tokens: the core ``inline`` stage never contributes
        to them, so a fence inventory parses only the block structure.

        Returns:
            The cached block-only ``MarkdownIt`` instance.

        """
        parser = FlextCliUtilitiesMarkdownParsing._VerbatimMarkdownIt(
            c.Cli.MARKDOWN_PARSER_PRESET,
        )
        parser.enable(list(c.Cli.MARKDOWN_PARSER_RULES))
        parser.core.ruler.disable(c.Cli.MARKDOWN_INLINE_CORE_RULE)
        return parser

    @staticmethod
    def _markdown_inline_walk(
        text: str,
        visit: Callable[[Token, int, str], None],
    ) -> None:
        """Visit inline children with their source line and preceding line text."""
        for block in FlextCliUtilitiesMarkdownParsing._markdown_tokens(text):
            if (
                block.type != c.Cli.MarkdownTokenType.INLINE
                or block.map is None
                or not block.children
            ):
                continue
            line = block.map[0] + 1
            prefix = ""
            for child in block.children:
                if child.type in c.Cli.MARKDOWN_LINE_BREAK_TOKENS:
                    line += 1
                    prefix = ""
                    continue
                visit(child, line, prefix)
                prefix += child.content


__all__: list[str] = ["FlextCliUtilitiesMarkdownParsing"]
