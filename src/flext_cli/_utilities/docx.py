"""Lightweight public utility boundary for generic DOCX bytes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m, p, t
from flext_cli._utilities import (
    FlextCliUtilitiesDocxReader,
    FlextCliUtilitiesDocxRenderer,
)


class FlextCliUtilitiesDocx:
    """Load the DOCX adapter only when a document operation executes."""

    @staticmethod
    def docx_read(source: bytes) -> p.Result[m.Cli.DocxDocumentPlan]:
        """Read document bytes through the causal DOCX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.DocxDocumentPlan]``.

        """
        return FlextCliUtilitiesDocxReader.docx_read(source)

    @staticmethod
    def docx_render(
        request: m.Cli.DocxRenderRequest,
    ) -> p.Result[m.Cli.DocxRenderResult]:
        """Render a typed document through the causal DOCX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.DocxRenderResult]``.

        """
        return FlextCliUtilitiesDocxRenderer.docx_render(request)


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesDocx",)
