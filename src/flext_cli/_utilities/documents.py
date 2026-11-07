"""Lightweight public utility boundary for DOCX and PPTX bytes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p
from flext_cli._utilities import _documents


class FlextCliUtilitiesDocuments:
    """Load python-docx and python-pptx only when a document operation runs."""

    @staticmethod
    def docx_read(source: bytes) -> p.Result[p.Cli.DocxDocumentPlan]:
        """Read document bytes through the DOCX adapter.

        Returns:
            The resulting ``p.Result[p.Cli.DocxDocumentPlan]``.

        """
        return _documents.FlextCliUtilitiesDocxReader.docx_read(source)

    @staticmethod
    def docx_render(
        request: p.Cli.DocxRenderRequest,
    ) -> p.Result[p.Cli.DocxRenderResult]:
        """Render a typed document through the DOCX adapter.

        Returns:
            The resulting ``p.Result[p.Cli.DocxRenderResult]``.

        """
        return _documents.FlextCliUtilitiesDocxRenderer.docx_render(request)

    @staticmethod
    def read_presentation(source: bytes) -> p.Result[p.Cli.PptxPresentationPlan]:
        """Read presentation bytes through the PPTX adapter.

        Returns:
            The resulting ``p.Result[p.Cli.PptxPresentationPlan]``.

        """
        return _documents.FlextCliUtilitiesPptxReader.read_presentation(source)

    @staticmethod
    def render_presentation(
        request: p.Cli.PptxRenderRequest,
    ) -> p.Result[p.Cli.PptxRenderResult]:
        """Render typed slides through the PPTX adapter.

        Returns:
            The resulting ``p.Result[p.Cli.PptxRenderResult]``.

        """
        return _documents.FlextCliUtilitiesPptxRenderer.render_presentation(request)


__all__: list[str] = ["FlextCliUtilitiesDocuments"]
