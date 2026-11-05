"""Aggregate plans and byte-boundary results for generic PPTX rendering.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_core import m

from flext_cli import c, p, t
from flext_cli._models._base.flextclimodelsbase_part_05 import FlextCliModelsBasePart05


class FlextCliModelsPptxPresentation:
    """Immutable presentation, slide, and render request/result models."""

    # NOTE (multi-agent, mro-j2yt.1): consumers exchange only validated plans
    # and bytes; python-pptx implementation objects never cross this boundary.

    class PptxSlidePlan(m.FrozenModel):
        title: str = m.Field(default="", description="Slide title.")

    class PptxPresentationPlan(m.FrozenModel):
        slides: tuple[FlextCliModelsPptxPresentation.PptxSlidePlan, ...] = m.Field(
            default=(),
            strict=False,
            description="Presentation slides.",
        )
        core_properties: t.JsonMapping = m.Field(
            default_factory=lambda: c.Cli.EMPTY_JSON_MAPPING,
            description="Core document properties.",
        )

    class PptxRenderRequest(FlextCliModelsBasePart05.OfficeRenderRequest):
        plan: Annotated[
            p.Cli.PptxPresentationPlan,
            t.schema_for_model(
                lambda: FlextCliModelsPptxPresentation.PptxPresentationPlan
            ),
        ] = m.Field(
            description="Validated presentation plan.",
        )

    class PptxRenderResult(FlextCliModelsBasePart05.OfficeRenderResult):
        plan: Annotated[
            p.Cli.PptxPresentationPlan,
            t.schema_for_model(
                lambda: FlextCliModelsPptxPresentation.PptxPresentationPlan
            ),
        ] = m.Field(
            description="Exact source plan.",
        )


__all__: tuple[str, ...] = ("FlextCliModelsPptxPresentation",)
