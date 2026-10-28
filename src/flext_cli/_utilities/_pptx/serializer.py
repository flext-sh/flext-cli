"""Generic PPTX byte serializer and object opener.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing import TYPE_CHECKING

from flext_cli import c, p
from flext_cli._utilities import FlextCliUtilitiesFiles

if TYPE_CHECKING:
    from pptx.presentation import Presentation as PresentationType


class FlextCliUtilitiesPptxSerializer:
    """Serialize and deserialize PPTX presentation objects."""

    # NOTE (multi-agent, mro-j2yt.1): consumers may pass python-pptx objects
    # inside this boundary; only bytes leave the boundary.

    @classmethod
    def pptx_save(cls, presentation: PresentationType) -> p.Result[bytes]:
        """Serialize a presentation object to bytes.

        Returns:
            The resulting ``p.Result[bytes]``.

        """
        return FlextCliUtilitiesFiles.files_save_bytes(
            presentation.save, str(c.Cli.PptxError.SERIALIZE_FAILED)
        )


__all__: tuple[str, ...] = ("FlextCliUtilitiesPptxSerializer",)
