"""Model-driven PPTX rendering and reading contract tests."""

from __future__ import annotations

from flext_cli import cli, m
from flext_tests import tm


def test_pptx_render_empty_presentation() -> None:
    """Rendering an empty plan produces a valid PPTX."""
    plan = m.Cli.PptxPresentationPlan()
    rendered = tm.ok(cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan)))
    tm.that(rendered.content[:2], eq=b"PK")
    restored = tm.ok(cli.pptx_read(rendered.content))
    tm.that(len(restored.slides), eq=0)


def test_pptx_render_with_slides() -> None:
    """Rendered slides contain the supplied titles."""
    plan = m.Cli.PptxPresentationPlan(
        slides=(m.Cli.PptxSlidePlan(title="Hello"), m.Cli.PptxSlidePlan(title="World"))
    )
    rendered = tm.ok(cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan)))
    restored = tm.ok(cli.pptx_read(rendered.content))
    tm.that(tuple(slide.title for slide in restored.slides), eq=("Hello", "World"))


def test_pptx_render_core_properties() -> None:
    """Core presentation properties are embedded in the rendered bytes."""
    plan = m.Cli.PptxPresentationPlan(
        slides=(m.Cli.PptxSlidePlan(title="Slide"),),
        core_properties={"title": "Test Title", "author": "Test Author"},
    )
    rendered = tm.ok(cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan)))
    restored = tm.ok(cli.pptx_read(rendered.content))
    tm.that(restored.core_properties["title"], eq="Test Title")
    tm.that(restored.core_properties["author"], eq="Test Author")


def test_pptx_read_round_trip() -> None:
    """Reading rendered bytes reproduces the presentation plan."""
    plan = m.Cli.PptxPresentationPlan(
        slides=(m.Cli.PptxSlidePlan(title="Hello"), m.Cli.PptxSlidePlan(title="World"))
    )
    render_result = cli.pptx_render(m.Cli.PptxRenderRequest(plan=plan))
    tm.that(render_result.success, eq=True, msg=render_result.error)
    read_result = cli.pptx_read(render_result.value.content)
    tm.that(read_result.success, eq=True, msg=read_result.error)
    tm.that(read_result.value.slides[0].title, eq="Hello")
    tm.that(read_result.value.slides[1].title, eq="World")


def test_pptx_read_rejects_invalid_bytes() -> None:
    """Reading invalid bytes returns a failure result."""
    result = cli.pptx_read(b"not a pptx")
    tm.that(result.success, eq=False)
    tm.that(result.error, ne=None)
