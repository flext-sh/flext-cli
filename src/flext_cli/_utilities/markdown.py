"""Markdown structure queries backed by markdown-it-py — ``u.Cli.markdown_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import itertools
import textwrap
from collections.abc import Callable
from functools import cache
from typing import TYPE_CHECKING, override

from markdown_it import MarkdownIt

from flext_cli import c, m, t

if TYPE_CHECKING:
    from markdown_it.token import Token


class FlextCliUtilitiesMarkdown:
    """Token-level Markdown inventory and fence rewriting."""

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
        parser = FlextCliUtilitiesMarkdown._VerbatimMarkdownIt(
            c.Cli.MARKDOWN_PARSER_PRESET,
        )
        return parser.enable(list(c.Cli.MARKDOWN_PARSER_RULES))

    @staticmethod
    def _markdown_tokens(text: str) -> t.SequenceOf[Token]:
        """Parse one Markdown document into its block token stream.

        Returns:
            The parsed block tokens.

        """
        return FlextCliUtilitiesMarkdown._markdown_parser().parse(text)

    @staticmethod
    def markdown_fences(text: str) -> t.SequenceOf[m.Cli.MarkdownFence]:
        """Return every fenced code block in document order.

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
            for token in FlextCliUtilitiesMarkdown._markdown_tokens(text)
            if token.type == c.Cli.MarkdownTokenType.FENCE and token.map is not None
        )

    @staticmethod
    def _markdown_inline_walk(
        text: str,
        visit: Callable[[Token, int, str], None],
    ) -> None:
        """Visit inline children with their source line and preceding line text."""
        for block in FlextCliUtilitiesMarkdown._markdown_tokens(text):
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

    @staticmethod
    def markdown_links(text: str) -> t.SequenceOf[m.Cli.MarkdownLink]:
        """Return inline, reference, and image destinations; autolinks excluded.

        Returns:
            The located link destinations.

        """
        links: t.MutableSequenceOf[m.Cli.MarkdownLink] = []

        def collect(child: Token, line: int, _prefix: str) -> None:
            if child.type == c.Cli.MarkdownTokenType.LINK_OPEN and child.markup not in {
                c.Cli.MARKDOWN_AUTOLINK_MARKUP,
                c.Cli.MARKDOWN_LINKIFY_MARKUP,
            }:
                links.append(
                    m.Cli.MarkdownLink(target=str(child.attrs["href"]), line=line),
                )
            elif child.type == c.Cli.MarkdownTokenType.IMAGE:
                links.append(
                    m.Cli.MarkdownLink(
                        target=str(child.attrs["src"]),
                        line=line,
                        image=True,
                    ),
                )

        FlextCliUtilitiesMarkdown._markdown_inline_walk(text, collect)
        return tuple(links)

    @staticmethod
    def _markdown_link_spans(
        lines: t.SequenceOf[str],
        links: t.SequenceOf[m.Cli.MarkdownLink],
    ) -> t.SequenceOf[t.Pair[m.Cli.MarkdownLink, t.Quad[int, int, int, int]]]:
        """Locate inline link spans as ``(label_start, target_start, target_end, end)``.

        Reference-style links carry no inline destination and are not located.

        Returns:
            The located links with their column offsets on their source line.

        """
        located: t.MutableSequenceOf[
            t.Pair[m.Cli.MarkdownLink, t.Quad[int, int, int, int]]
        ] = []
        cursors: t.MutableMappingKV[int, int] = {}
        for link in links:
            line = lines[link.line - 1]
            cursor = cursors.get(link.line, 0)
            found = next(
                (
                    (position, position + len(opener), position + len(prefix))
                    for prefix, opener in (
                        ("](<", f"](<{link.target}>"),
                        ("](", f"]({link.target}"),
                    )
                    for position in (line.find(opener, cursor),)
                    if position >= 0
                ),
                None,
            )
            if found is None:
                continue
            label_end, after_target, target_start = found
            depth = 0
            label_start = label_end
            while label_start > 0:
                label_start -= 1
                if line[label_start] == "]":
                    depth += 1
                elif line[label_start] == "[":
                    if depth == 0:
                        break
                    depth -= 1
            if link.image and label_start > 0 and line[label_start - 1] == "!":
                label_start -= 1
            end = line.find(")", after_target)
            if end < 0:
                continue
            located.append((
                link,
                (label_start, target_start, target_start + len(link.target), end + 1),
            ))
            cursors[link.line] = end + 1
        return located

    @staticmethod
    def markdown_rewrite_link_targets(
        text: str,
        rewrite: Callable[[m.Cli.MarkdownLink], str | None],
    ) -> t.Pair[str, int]:
        """Replace inline link destinations in place; labels stay byte-identical.

        Returns:
            The rewritten document and the number of replaced destinations.

        """
        lines = text.splitlines(keepends=True)
        spans = FlextCliUtilitiesMarkdown._markdown_link_spans(
            lines,
            FlextCliUtilitiesMarkdown.markdown_links(text),
        )
        replaced = 0
        for link, (_label_start, target_start, target_end, _end) in reversed(spans):
            target = rewrite(link)
            if target is None or target == link.target:
                continue
            index = link.line - 1
            lines[index] = (
                f"{lines[index][:target_start]}{target}{lines[index][target_end:]}"
            )
            replaced += 1
        return ("".join(lines), replaced)

    @staticmethod
    def markdown_unlink(
        text: str,
        unlink: Callable[[m.Cli.MarkdownLink], bool],
    ) -> str:
        """Replace selected inline links with their authored label text.

        Returns:
            The rewritten document.

        """
        lines = text.splitlines(keepends=True)
        spans = FlextCliUtilitiesMarkdown._markdown_link_spans(
            lines,
            FlextCliUtilitiesMarkdown.markdown_links(text),
        )
        for link, (label_start, target_start, _target_end, end) in reversed(spans):
            if not unlink(link):
                continue
            index = link.line - 1
            line = lines[index]
            label_open = label_start + (2 if link.image else 1)
            label_close = line.rfind("](", label_open, target_start)
            lines[index] = (
                f"{line[:label_start]}{line[label_open:label_close]}{line[end:]}"
            )
        return "".join(lines)

    @staticmethod
    def markdown_code_spans(text: str) -> t.SequenceOf[m.Cli.MarkdownCodeSpan]:
        """Return inline code spans with the prose preceding them on their line.

        Returns:
            The located code spans.

        """
        spans: t.MutableSequenceOf[m.Cli.MarkdownCodeSpan] = []

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
    def markdown_headings(text: str) -> t.SequenceOf[m.Cli.MarkdownHeading]:
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
    def _markdown_wrap_line(line: str, width: int) -> t.StrSequence:
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
        replacements: t.MappingKV[m.Cli.MarkdownFence, t.StrPair],
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
