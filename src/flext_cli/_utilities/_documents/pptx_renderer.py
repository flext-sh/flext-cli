"""Generic model-driven PPTX renderer.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import BytesIO

from flext_core import r
from pptx import Presentation
from pptx.presentation import Presentation as PresentationType

from flext_cli import c, m, p, t
from flext_cli._utilities._documents.pptx_serializer import (
    FlextCliUtilitiesPptxSerializer,
)
from flext_cli._utilities._files.native_results import (
    FlextCliUtilitiesFilesNativeResults,
)


class FlextCliUtilitiesPptxRenderer:
    """Render one immutable presentation plan into PPTX bytes."""

    # NOTE (multi-agent, mro-j2yt.1): python-pptx objects stay inside this
    # module; consumers exchange only validated plans and bytes.

    @classmethod
    def render_presentation(
        cls,
        request: p.Cli.PptxRenderRequest,
    ) -> p.Result[p.Cli.PptxRenderResult]:
        """Render typed slides into presentation bytes.

        Returns:
            The resulting ``p.Result[p.Cli.PptxRenderResult]``.

        """
        presentation_result = cls._presentation_for_request(request)
        if presentation_result.failure:
            return r[p.Cli.PptxRenderResult].from_failure(presentation_result)
        presentation = presentation_result.value
        try:
            cls._apply_presentation(presentation, request.plan)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.PptxRenderResult].fail(
                f"{c.Cli.PptxError.RENDER_FAILED}: {detail}",
            )
        content = FlextCliUtilitiesPptxSerializer.pptx_save(presentation)
        if content.failure:
            return r[p.Cli.PptxRenderResult].from_failure(content)
        return r[p.Cli.PptxRenderResult].ok(
            m.Cli.PptxRenderResult.model_validate({
                "content": content.value,
                "plan": request.plan,
            }),
        )

    @classmethod
    def _presentation_for_request(
        cls,
        request: p.Cli.PptxRenderRequest,
    ) -> p.Result[PresentationType]:
        if request.template is None:
            return r[PresentationType].ok(Presentation())
        return FlextCliUtilitiesFilesNativeResults.coded_result(
            Presentation,
            c.Cli.PptxError.PRESENTATION_LOAD_FAILED,
            (OSError, ValueError, KeyError),
        )(BytesIO(request.template))

    @classmethod
    def _apply_presentation(
        cls,
        presentation: PresentationType,
        plan: p.Cli.PptxPresentationPlan,
    ) -> None:
        cls._apply_pptx_core_properties(presentation, plan.core_properties)
        for slide in plan.slides:
            cls._apply_slide(presentation, slide)

    @classmethod
    def _apply_pptx_core_properties(
        cls,
        presentation: PresentationType,
        properties: t.JsonMapping,
    ) -> None:
        core_props = presentation.core_properties
        for key, value in properties.items():
            if hasattr(core_props, key):
                setattr(core_props, key, value)

    @classmethod
    def _apply_slide(
        cls,
        presentation: PresentationType,
        plan: p.Cli.PptxSlidePlan,
    ) -> None:
        layout = presentation.slide_layouts[0]
        new_slide = presentation.slides.add_slide(layout)
        if new_slide.shapes.title is not None:
            new_slide.shapes.title.text = plan.title


__all__: tuple[str, ...] = ("FlextCliUtilitiesPptxRenderer",)
