"""Model-driven PPTX rendering and reading contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import m, tm, u


class TestsFlextCliPptxRender:
    """Behavioral contract validated by this module."""

    @staticmethod
    def test_pptx_render_empty_presentation() -> None:
        """Rendering an empty plan produces a valid PPTX."""
        plan = m.Cli.PptxPresentationPlan()
        rendered = tm.ok(u.Cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan)))
        tm.that(rendered.content[:2], eq=b"PK")
        restored = tm.ok(u.Cli.pptx_read(rendered.content))
        tm.that(len(restored.slides), eq=0)

    @staticmethod
    def test_pptx_render_with_slides() -> None:
        """Rendered slides contain the supplied titles."""
        plan = m.Cli.PptxPresentationPlan(
            slides=(
                m.Cli.PptxSlidePlan(title="Hello"),
                m.Cli.PptxSlidePlan(title="World"),
            ),
        )
        rendered = tm.ok(u.Cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan)))
        restored = tm.ok(u.Cli.pptx_read(rendered.content))
        tm.that(tuple(slide.title for slide in restored.slides), eq=("Hello", "World"))

    @staticmethod
    def test_pptx_render_core_properties() -> None:
        """Core presentation properties are embedded in the rendered bytes."""
        plan = m.Cli.PptxPresentationPlan(
            slides=(m.Cli.PptxSlidePlan(title="Slide"),),
            core_properties={"title": "Test Title", "author": "Test Author"},
        )
        rendered = tm.ok(u.Cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan)))
        restored = tm.ok(u.Cli.pptx_read(rendered.content))
        tm.that(restored.core_properties["title"], eq="Test Title")
        tm.that(restored.core_properties["author"], eq="Test Author")

    @staticmethod
    def test_pptx_read_round_trip() -> None:
        """Reading rendered bytes reproduces the presentation plan."""
        plan = m.Cli.PptxPresentationPlan(
            slides=(
                m.Cli.PptxSlidePlan(title="Hello"),
                m.Cli.PptxSlidePlan(title="World"),
            ),
        )
        render_result = u.Cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan))
        tm.that(render_result.success, eq=True, msg=render_result.error)
        read_result = u.Cli.pptx_read(render_result.value.content)
        tm.that(read_result.success, eq=True, msg=read_result.error)
        tm.that(read_result.value.slides[0].title, eq="Hello")
        tm.that(read_result.value.slides[1].title, eq="World")

    @staticmethod
    def test_pptx_read_rejects_invalid_bytes() -> None:
        """Reading invalid bytes returns a failure result."""
        result = u.Cli.pptx_read(b"not a pptx")
        tm.fail(result.success)
        tm.that(result.error, ne=None)


__all__: list[str] = ["TestsFlextCliPptxRender"]
