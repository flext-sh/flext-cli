"""Generic PPTX byte serializer and object opener."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from flext_cli import c, p, r

if TYPE_CHECKING:
    from pptx.presentation import Presentation as PresentationType


class FlextCliUtilitiesPptxSerializer:
    """Serialize and deserialize PPTX presentation objects."""

    # NOTE (multi-agent, mro-j2yt.1): consumers may pass python-pptx objects
    # inside this boundary; only bytes leave the boundary.

    @classmethod
    def pptx_save(cls, presentation: PresentationType) -> p.Result[bytes]:
        """Serialize a presentation object to bytes."""
        target = BytesIO()
        try:
            presentation.save(target)
        except (OSError, TypeError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[bytes].fail(f"{c.Cli.PptxError.SERIALIZE_FAILED}: {detail}")
        content = target.getvalue()
        if not content:
            return r[bytes].fail(str(c.Cli.PptxError.SERIALIZE_FAILED))
        return r[bytes].ok(content)

__all__: tuple[str, ...] = ("FlextCliUtilitiesPptxSerializer",)
