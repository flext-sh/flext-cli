"""Markdown structure queries backed by markdown-it-py — ``u.Cli.markdown_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import itertools
import textwrap
from collections.abc import Mapping, MutableSequence, Sequence
from typing import TYPE_CHECKING

from flext_cli import c, m, p
from flext_cli._utilities.markdown_links import FlextCliUtilitiesMarkdownLinks

if TYPE_CHECKING:
    from markdown_it.token import Token


class FlextCliUtilitiesMarkdown(FlextCliUtilitiesMarkdownLinks):
    """Token-level Markdown inventory and fence rewriting."""

    @staticmethod
    def markdown_fences(text: str) -> Sequence[p.Cli.MarkdownFence]:
        """Return every fenced code block in document order.

        Only the block structure is parsed; inline content plays no part in
        a fence.

        Returns:
            The located fences.

        """
        return tuple(
            m.Cli.MarkdownFence(
                info=token.info,
                language=token.info.strip().partition(" ")[0].lower(),
                code=token.content,
                opening_line=token.map[0] + 1,
                closing_line=token.map[1],
                nested=token.level > 0,
            )
            for token in FlextCliUtilitiesMarkdown._markdown_block_parser().parse(text)
            if token.type == c.Cli.MarkdownTokenType.FENCE and token.map is not None
        )

    @staticmethod
    def markdown_code_spans(text: str) -> Sequence[p.Cli.MarkdownCodeSpan]:
        """Return inline code spans with the prose preceding them on their line.

        Returns:
            The located code spans.

        """
        spans: MutableSequence[p.Cli.MarkdownCodeSpan] = []

        def collect(child: Token, line: int, prefix: str) -> None:
            if child.type == c.Cli.MarkdownTokenType.CODE_INLINE:
                spans.append(
                    m.Cli.MarkdownCodeSpan(
                        content=child.content,
                        prefix=prefix,
                        line=line,
                    ),
                )

        FlextCliUtilitiesMarkdown._markdown_inline_walk(text, collect)
        return tuple(spans)

    @staticmethod
    def markdown_headings(text: str) -> Sequence[p.Cli.MarkdownHeading]:
        """Return headings with their source text in document order.

        Returns:
            The located headings.

        """
        tokens = FlextCliUtilitiesMarkdown._markdown_tokens(text)
        return tuple(
            m.Cli.MarkdownHeading(
                level=int(opening.tag[1:]),
                text=inline.content.strip(),
                line=opening.map[0] + 1,
            )
            for opening, inline in itertools.pairwise(tokens)
            if opening.type == c.Cli.MarkdownTokenType.HEADING_OPEN
            and opening.map is not None
        )

    @staticmethod
    def _markdown_wrap_line(line: str, width: int) -> Sequence[str]:
        """Wrap one prose line without changing its Markdown structure.

        Returns:
            The wrapped lines; structural or short lines stay untouched.

        """
        stripped = line.lstrip()
        if (
            len(line) <= width
            or not stripped
            or stripped != line
            or stripped.startswith(tuple(c.Cli.MARKDOWN_WRAP_STRUCTURAL_PREFIXES))
        ):
            return (line,)
        prefix = ""
        body = line
        if line.startswith((
            *c.Cli.MARKDOWN_WRAP_BULLET_MARKERS,
            c.Cli.MARKDOWN_WRAP_QUOTE_MARKER,
        )):
            prefix, body = line[:2], line[2:]
        else:
            marker, separator, remainder = line.partition(" ")
            if separator and marker.endswith(".") and marker[:-1].isdigit():
                prefix, body = f"{marker} ", remainder
        indent = (
            prefix if prefix == c.Cli.MARKDOWN_WRAP_QUOTE_MARKER else " " * len(prefix)
        )
        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=prefix,
            subsequent_indent=indent,
            break_long_words=False,
            break_on_hyphens=False,
        )
        return tuple(wrapper.wrap(body)) or (line,)

    @staticmethod
    def markdown_wrap(
        value: str, width: int = c.Cli.MARKDOWN_WRAP_DEFAULT_WIDTH
    ) -> str:
        """Wrap prose lines to ``width`` while keeping fenced code verbatim.

        Registered as the ``markdown_wrap`` Jinja filter of the template owner.

        Returns:
            The document with overlong prose lines reflowed.

        """
        verbatim = frozenset(
            number
            for fence in FlextCliUtilitiesMarkdown.markdown_fences(value)
            for number in range(fence.opening_line, fence.closing_line + 1)
        )
        return "\n".join(
            wrapped
            for number, line in enumerate(value.split("\n"), start=1)
            for wrapped in (
                (line,)
                if number in verbatim
                else FlextCliUtilitiesMarkdown._markdown_wrap_line(line, width)
            )
        )

    @staticmethod
    def markdown_rewrite_fences(
        text: str,
        replacements: Mapping[p.Cli.MarkdownFence, tuple[str, str]],
    ) -> str:
        """Splice ``(info, code)`` replacements for fences parsed from ``text``.

        Callers parse once with ``markdown_fences`` and pass the fences they
        replace; prose, other fences, fence markers, and container prefixes
        (list indentation or quote markers) stay byte-identical.

        Returns:
            The rewritten document.

        """
        lines = text.splitlines(keepends=True)
        for fence in sorted(replacements, key=lambda item: -item.opening_line):
            info, body = replacements[fence]
            start = fence.opening_line - 1
            opening = lines[start]
            marker_at = min(
                position
                for position in (
                    opening.find(mark) for mark in c.Cli.MARKDOWN_FENCE_MARKS
                )
                if position >= 0
            )
            stripped = opening[marker_at:]
            markup = stripped[: len(stripped) - len(stripped.lstrip(stripped[0]))]
            continuation = "".join(
                char if char in c.Cli.MARKDOWN_CONTAINER_CHARS else " "
                for char in opening[:marker_at]
            )
            newline = opening[len(opening.rstrip("\r\n")) :] or "\n"
            closed = fence.closing_line - 1 > start and (
                lines[fence.closing_line - 1]
                .lstrip(c.Cli.MARKDOWN_CONTAINER_CHARS)
                .startswith(markup)
            )
            if body and not body.endswith("\n"):
                body = f"{body}{newline}"
            replacement = [f"{opening[:marker_at]}{markup}{info}{newline}"]
            replacement.extend(
                f"{continuation}{body_line}"
                if body_line.strip()
                else f"{continuation.rstrip()}{body_line}"
                for body_line in body.splitlines(keepends=True)
            )
            if not closed:
                replacement.append(f"{continuation}{markup}{newline}")
            body_end = fence.closing_line - 1 if closed else fence.closing_line
            lines[start:body_end] = replacement
        return "".join(lines)


__all__: list[str] = ["FlextCliUtilitiesMarkdown"]
