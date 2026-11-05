"""Markdown link inventory and in-place link rewriting — ``u.Cli.markdown_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, MutableMapping, MutableSequence, Sequence
from typing import TYPE_CHECKING

from flext_cli import c, m, p
from flext_cli._utilities.markdown_parsing import FlextCliUtilitiesMarkdownParsing

if TYPE_CHECKING:
    from markdown_it.token import Token


class FlextCliUtilitiesMarkdownLinks(FlextCliUtilitiesMarkdownParsing):
    """Locate and rewrite inline link destinations without touching labels."""

    @staticmethod
    def markdown_links(text: str) -> Sequence[p.Cli.MarkdownLink]:
        """Return inline, reference, and image destinations; autolinks excluded.

        Returns:
            The located link destinations.

        """
        links: MutableSequence[p.Cli.MarkdownLink] = []

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

        FlextCliUtilitiesMarkdownLinks._markdown_inline_walk(text, collect)
        return tuple(links)

    @staticmethod
    def _markdown_link_spans(
        lines: Sequence[str],
        links: Sequence[p.Cli.MarkdownLink],
    ) -> Sequence[tuple[p.Cli.MarkdownLink, tuple[int, int, int, int]]]:
        """Locate inline link spans as ``(label_start, target_start, target_end, end)``.

        Reference-style links carry no inline destination and are not located.

        Returns:
            The located links with their column offsets on their source line.

        """
        located: MutableSequence[
            tuple[p.Cli.MarkdownLink, tuple[int, int, int, int]]
        ] = []
        cursors: MutableMapping[int, int] = {}
        for link in links:
            line = lines[link.line - 1]
            found = FlextCliUtilitiesMarkdownLinks._link_opener(
                line, link.target, cursors.get(link.line, 0)
            )
            if found is None:
                continue
            label_end, after_target, target_start = found
            end = line.find(")", after_target)
            if end < 0:
                continue
            located.append((
                link,
                (
                    FlextCliUtilitiesMarkdownLinks._label_start(
                        line, label_end, image=link.image
                    ),
                    target_start,
                    target_start + len(link.target),
                    end + 1,
                ),
            ))
            cursors[link.line] = end + 1
        return located

    @staticmethod
    def _link_opener(
        line: str,
        target: str,
        cursor: int,
    ) -> tuple[int, int, int] | None:
        """Find the next inline opener of one destination after ``cursor``.

        The angle-bracket form is preferred over the bare form.

        Returns:
            The label end, the position after the destination, and the
            destination start, or ``None`` when no opener follows.

        """
        for prefix, opener in (("](<", f"](<{target}>"), ("](", f"]({target}")):
            position = line.find(opener, cursor)
            if position >= 0:
                return position, position + len(opener), position + len(prefix)
        return None

    @staticmethod
    def _label_start(line: str, label_end: int, *, image: bool) -> int:
        """Walk back from one label end to its balanced opening bracket.

        Returns:
            The label start column, including the image marker of an image.

        """
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
        if image and label_start > 0 and line[label_start - 1] == "!":
            label_start -= 1
        return label_start

    @staticmethod
    def markdown_rewrite_link_targets(
        text: str,
        rewrite: Callable[[p.Cli.MarkdownLink], str | None],
    ) -> tuple[str, int]:
        """Replace inline link destinations in place; labels stay byte-identical.

        Returns:
            The rewritten document and the number of replaced destinations.

        """
        lines = text.splitlines(keepends=True)
        spans = FlextCliUtilitiesMarkdownLinks._markdown_link_spans(
            lines,
            FlextCliUtilitiesMarkdownLinks.markdown_links(text),
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
        unlink: Callable[[p.Cli.MarkdownLink], bool],
    ) -> str:
        """Replace selected inline links with their authored label text.

        Returns:
            The rewritten document.

        """
        lines = text.splitlines(keepends=True)
        spans = FlextCliUtilitiesMarkdownLinks._markdown_link_spans(
            lines,
            FlextCliUtilitiesMarkdownLinks.markdown_links(text),
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


__all__: list[str] = ["FlextCliUtilitiesMarkdownLinks"]
