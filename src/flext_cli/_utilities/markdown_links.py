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
        touched: set[int] = set()
        for link, (_label_start, target_start, target_end, _end) in reversed(spans):
            target = rewrite(link)
            if target is None or target == link.target:
                continue
            index = link.line - 1
            lines[index] = (
                f"{lines[index][:target_start]}{target}{lines[index][target_end:]}"
            )
            touched.add(index)
            replaced += 1
        FlextCliUtilitiesMarkdownLinks._markdown_realign_tables(text, lines, touched)
        return ("".join(lines), replaced)

    @staticmethod
    def markdown_unlink(
        text: str,
        unlink: Callable[[p.Cli.MarkdownLink], bool],
    ) -> str:
        """Replace selected inline links with their authored label text.

        A GFM table whose cells shrink is re-aligned, so an aligned source
        stays aligned.

        Returns:
            The rewritten document.

        """
        lines = text.splitlines(keepends=True)
        spans = FlextCliUtilitiesMarkdownLinks._markdown_link_spans(
            lines,
            FlextCliUtilitiesMarkdownLinks.markdown_links(text),
        )
        touched: set[int] = set()
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
            touched.add(index)
        FlextCliUtilitiesMarkdownLinks._markdown_realign_tables(text, lines, touched)
        return "".join(lines)

    @staticmethod
    def markdown_align_tables(text: str) -> str:
        """Align every GFM table of ``text`` in the Markdown gate's table style.

        Generators render tables through this owner, so their output is
        aligned by construction instead of formatted afterwards.

        Returns:
            ``text`` with each table's columns padded to their widest cell.

        """
        lines = text.splitlines(keepends=True)
        FlextCliUtilitiesMarkdownLinks._markdown_realign_tables(text, lines, None)
        return "".join(lines)

    @staticmethod
    def _markdown_realign_tables(
        text: str,
        lines: MutableSequence[str],
        touched: set[int] | None,
    ) -> None:
        """Re-align in place the GFM tables of ``text`` with a rewritten row.

        Rewrites keep the line count, so the table line ranges of the source
        address ``lines``. Columns pad to their widest cell, as the aligned
        table style of the Markdown gate formats them. ``None`` selects every
        table of ``text``.
        """
        if touched is not None and not touched:
            return
        for token in FlextCliUtilitiesMarkdownLinks._markdown_tokens(text):
            if token.type != c.Cli.MarkdownTokenType.TABLE_OPEN or token.map is None:
                continue
            start, end = token.map
            if touched is not None and touched.isdisjoint(range(start, end)):
                continue
            lines[start:end] = FlextCliUtilitiesMarkdownLinks._markdown_aligned_rows(
                lines[start:end],
            )

    @staticmethod
    def _markdown_table_cells(row: str) -> Sequence[str]:
        """Split one table row on its unescaped pipes.

        Returns:
            The stripped cell texts, outer pipes excluded.

        """
        body = row.strip().removeprefix("|").removesuffix("|")
        cells: MutableSequence[str] = []
        current: MutableSequence[str] = []
        escaped = False
        for char in body:
            if char == "|" and not escaped:
                cells.append("".join(current).strip())
                current = []
            else:
                current.append(char)
            escaped = char == "\\" and not escaped
        cells.append("".join(current).strip())
        return tuple(cells)

    @staticmethod
    def _markdown_aligned_rows(rows: Sequence[str]) -> Sequence[str]:
        """Render table rows with every column padded to its widest cell.

        The delimiter row keeps its alignment colons; rows whose cell count
        differs from the delimiter are a malformed table and stay as written.

        Returns:
            The aligned rows, each keeping its original line ending.

        """
        split = FlextCliUtilitiesMarkdownLinks._markdown_table_cells
        cells = [split(row) for row in rows]
        delimiter = cells[1]
        if any(len(row) != len(delimiter) for row in cells):
            return rows
        widths = [
            max(
                c.Cli.MARKDOWN_TABLE_DELIMITER_MIN_WIDTH,
                *(len(row[column]) for index, row in enumerate(cells) if index != 1),
            )
            for column in range(len(delimiter))
        ]
        indent = rows[0][: len(rows[0]) - len(rows[0].lstrip())]
        rendered: MutableSequence[str] = []
        for index, (row, source) in enumerate(zip(cells, rows, strict=True)):
            ending = source[len(source.rstrip("\r\n")) :]
            parts = (
                (
                    (":" if mark.startswith(":") else "-")
                    + "-" * (width - 2)
                    + (":" if mark.endswith(":") else "-")
                )
                if index == 1
                else (
                    cell.rjust(width)
                    if delimiter[column].endswith(":")
                    and not delimiter[column].startswith(":")
                    else cell.center(width)
                    if delimiter[column].startswith(":")
                    and delimiter[column].endswith(":")
                    else cell.ljust(width)
                )
                for column, (cell, mark, width) in enumerate(
                    zip(row, delimiter, widths, strict=True)
                )
            )
            rendered.append(f"{indent}| {' | '.join(parts)} |{ending}")
        return tuple(rendered)


__all__: list[str] = ["FlextCliUtilitiesMarkdownLinks"]
