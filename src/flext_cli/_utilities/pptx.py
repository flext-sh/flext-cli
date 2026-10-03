"""Lightweight public utility boundary for generic PPTX bytes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import m, p, t


class FlextCliUtilitiesPptx:
    """Load the PPTX adapter only when a presentation operation executes."""

    @staticmethod
    def pptx_read(source: bytes) -> p.Result[m.Cli.PptxPresentationPlan]:
        """Read presentation bytes through the causal PPTX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.PptxPresentationPlan]``.

        """
        from flext_cli._utilities._pptx._reader import FlextCliUtilitiesPptxReader

        return FlextCliUtilitiesPptxReader.pptx_read(source)

    @staticmethod
    def pptx_render(
        request: m.Cli.PptxRenderRequest,
    ) -> p.Result[m.Cli.PptxRenderResult]:
        """Render a typed presentation through the causal PPTX adapter boundary.

        Returns:
            The resulting ``p.Result[m.Cli.PptxRenderResult]``.

        """
        from flext_cli._utilities._pptx._renderer import FlextCliUtilitiesPptxRenderer

        return FlextCliUtilitiesPptxRenderer.pptx_render(request)


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesPptx",)
