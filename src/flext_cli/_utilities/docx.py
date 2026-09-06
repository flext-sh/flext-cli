"""Lightweight public utility boundary for generic DOCX bytes."""

from __future__ import annotations

from flext_cli import m, p


class FlextCliUtilitiesDocx:
    """Load the DOCX adapter only when a document operation executes."""

    @staticmethod
    def docx_read(source: bytes) -> p.Result[m.Cli.DocxDocumentPlan]:
        """Read document bytes through the causal DOCX adapter boundary."""
        from ._docx._reader import FlextCliUtilitiesDocxReader

        return FlextCliUtilitiesDocxReader.docx_read(source)

    @staticmethod
    def docx_render(
        request: m.Cli.DocxRenderRequest,
    ) -> p.Result[m.Cli.DocxRenderResult]:
        """Render a typed document through the causal DOCX adapter boundary."""
        from ._docx._renderer import FlextCliUtilitiesDocxRenderer

        return FlextCliUtilitiesDocxRenderer.docx_render(request)


__all__: tuple[str, ...] = ("FlextCliUtilitiesDocx",)
