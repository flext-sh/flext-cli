"""Lightweight public utility boundary for generic PPTX bytes."""

from __future__ import annotations

from flext_cli import m, p


class FlextCliUtilitiesPptx:
    """Load the PPTX adapter only when a presentation operation executes."""

    @staticmethod
    def pptx_read(source: bytes) -> p.Result[m.Cli.PptxPresentationPlan]:
        """Read presentation bytes through the causal PPTX adapter boundary."""
        from ._pptx._reader import FlextCliUtilitiesPptxReader

        return FlextCliUtilitiesPptxReader.pptx_read(source)

    @staticmethod
    def pptx_render(
        request: m.Cli.PptxRenderRequest,
    ) -> p.Result[m.Cli.PptxRenderResult]:
        """Render a typed presentation through the causal PPTX adapter boundary."""
        from ._pptx._renderer import FlextCliUtilitiesPptxRenderer

        return FlextCliUtilitiesPptxRenderer.pptx_render(request)


__all__: tuple[str, ...] = ("FlextCliUtilitiesPptx",)
