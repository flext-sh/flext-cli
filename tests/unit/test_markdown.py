"""Behavioral tests for the public Markdown utility contract (``u.Cli.markdown_*``).

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import tm, u


class TestsFlextCliMarkdown:
    """Assert the observable contract of the ``u.Cli`` Markdown helpers."""

    _DOCUMENT = (
        "# Title\n"
        "\n"
        "Run `make check` and see [guide](docs/guide.md).\n"
        "Wrapped ![chart](img/c.png) and `[fake](x.md)` code.\n"
        "\n"
        "- item\n"
        "\n"
        "  ```python notest\n"
        "  value = 1\n"
        "  ```\n"
        "\n"
        "~~~bash\n"
        "echo [no](link.md)\n"
        "~~~\n"
        "\n"
        "[ref][r] and <https://example.com>\n"
        "\n"
        "[r]: docs/ref.md\n"
    )

    @staticmethod
    def test_fences_carry_language_body_lines_and_nesting() -> None:
        """Backtick and tilde fences are located with verbatim bodies."""
        fences = u.Cli.markdown_fences(TestsFlextCliMarkdown._DOCUMENT)
        tm.that(
            [
                (f.language, f.info, f.code, f.opening_line, f.closing_line, f.nested)
                for f in fences
            ],
            eq=[
                ("python", "python notest", "value = 1\n", 8, 10, True),
                ("bash", "bash", "echo [no](link.md)\n", 12, 14, False),
            ],
        )

    @staticmethod
    def test_links_exclude_code_and_autolinks_and_keep_lines() -> None:
        """Links inside code never surface; reference and image links do."""
        links = u.Cli.markdown_links(TestsFlextCliMarkdown._DOCUMENT)
        tm.that(
            [(link.target, link.line, link.image) for link in links],
            eq=[
                ("docs/guide.md", 3, False),
                ("img/c.png", 4, True),
                ("docs/ref.md", 16, False),
            ],
        )

    @staticmethod
    def test_link_destinations_are_verbatim() -> None:
        """Destinations keep spaces and characters exactly as authored."""
        links = u.Cli.markdown_links("[a](<my file.md>) [b](%7Ex.md)\n")
        tm.that([link.target for link in links], eq=["my file.md", "%7Ex.md"])

    @staticmethod
    def test_code_spans_report_preceding_prose() -> None:
        """Each span carries the rendered prose before it on its line."""
        spans = u.Cli.markdown_code_spans("**Run** `make check` then ``a ` b``\n")
        tm.that(
            [(span.content, span.prefix, span.line) for span in spans],
            eq=[("make check", "Run ", 1), ("a ` b", "Run make check then ", 1)],
        )

    @staticmethod
    def test_headings_cover_atx_and_setext() -> None:
        """ATX and setext headings are inventoried with level and line."""
        headings = u.Cli.markdown_headings("Top\n===\n\n## Next `x`\n")
        tm.that(
            [(h.level, h.text, h.line) for h in headings],
            eq=[(1, "Top", 1), (2, "Next `x`", 4)],
        )

    @staticmethod
    def test_rewrite_fences_keeps_container_prefix_and_prose() -> None:
        """A rewritten nested body keeps its list indentation; prose is unchanged."""
        document = TestsFlextCliMarkdown._DOCUMENT
        nested = u.Cli.markdown_fences(document)[0]
        rewritten = u.Cli.markdown_rewrite_fences(
            document,
            {nested: (nested.info, "value = 2\n\nother = 3")},
        )
        tm.that(
            rewritten,
            eq=document.replace("  value = 1\n", "  value = 2\n\n  other = 3\n"),
        )

    @staticmethod
    def test_rewrite_fences_inside_block_quote() -> None:
        """Quote markers are re-applied to every rewritten body line."""
        document = "> ```py\n> a\n> ```\n"
        (fence,) = u.Cli.markdown_fences(document)
        rewritten = u.Cli.markdown_rewrite_fences(document, {fence: ("python", "b\n")})
        tm.that(rewritten, eq="> ```python\n> b\n> ```\n")

    @staticmethod
    def test_rewrite_fences_closes_unterminated_fence() -> None:
        """An unterminated fence is closed after its rewritten body."""
        document = "text\n\n```python\nx=1\n"
        (fence,) = u.Cli.markdown_fences(document)
        rewritten = u.Cli.markdown_rewrite_fences(
            document,
            {fence: (fence.info, "x = 1\n")},
        )
        tm.that(rewritten, eq="text\n\n```python\nx = 1\n```\n")

    @staticmethod
    def test_rewrite_link_targets_counts_and_preserves_labels() -> None:
        """Only selected inline destinations change; code spans stay intact."""
        rewritten, count = u.Cli.markdown_rewrite_link_targets(
            "[a `x`](one) and [b](<two>) and `[c](one)`\n",
            lambda link: f"{link.target}.md" if link.target != "two" else None,
        )
        tm.that(
            (rewritten, count),
            eq=("[a `x`](one.md) and [b](<two>) and `[c](one)`\n", 1),
        )

    @staticmethod
    def test_unlink_keeps_label_and_images() -> None:
        """Selected links collapse to their label; images are untouched."""
        rewritten = u.Cli.markdown_unlink(
            "See [the `guide`](a.md), [web](https://x.io) ![i](a.png)\n",
            lambda link: not link.image and not link.target.startswith("https:"),
        )
        tm.that(rewritten, eq="See the `guide`, [web](https://x.io) ![i](a.png)\n")
