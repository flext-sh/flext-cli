"""Markdown structure models produced by the ``u.Cli.markdown_*`` parser.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing import Annotated

from flext_core import m


class FlextCliModelsMarkdown:
    """Markdown token projections, flat in ``m.Cli.*``.

    Line numbers are 1-based source lines; whitespace is preserved verbatim.
    """

    class MarkdownFence(m.ImmutableValueModel):
        """One fenced code block located in its Markdown source."""

        info: Annotated[str, m.Field(description="Raw fence info string")]
        language: Annotated[
            str,
            m.Field(description="Lower-cased first token of the info string"),
        ]
        code: Annotated[str, m.Field(description="Fence body, verbatim")]
        opening_line: Annotated[
            int,
            m.Field(ge=1, description="Source line of the opening fence"),
        ]
        closing_line: Annotated[
            int,
            m.Field(ge=1, description="Last source line the block occupies"),
        ]
        nested: Annotated[
            bool,
            m.Field(description="Whether the fence sits inside a list or quote"),
        ] = False

    class MarkdownLink(m.ImmutableValueModel):
        """One link or image destination with its source line."""

        target: Annotated[str, m.Field(description="Destination, verbatim")]
        line: Annotated[int, m.Field(ge=1, description="Source line of the link")]
        image: Annotated[
            bool,
            m.Field(description="Whether the token is an image"),
        ] = False

    class MarkdownHeading(m.ImmutableValueModel):
        """One ATX or setext heading with its plain text."""

        level: Annotated[int, m.Field(ge=1, le=6, description="Heading depth")]
        text: Annotated[str, m.Field(description="Plain heading text")]
        line: Annotated[int, m.Field(ge=1, description="Source line of the heading")]

    class MarkdownCodeSpan(m.ImmutableValueModel):
        """One inline code span with the prose that precedes it on its line."""

        content: Annotated[str, m.Field(description="Code span content")]
        prefix: Annotated[
            str,
            m.Field(description="Rendered prose preceding the span on its line"),
        ] = ""
        line: Annotated[int, m.Field(ge=1, description="Source line of the span")]


__all__: list[str] = ["FlextCliModelsMarkdown"]
