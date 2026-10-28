"""Document-independent color value declarations.

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

from typing import Annotated, Literal

from flext_core import m


class FlextCliModelsColor:
    """Shared immutable color values without document-domain dependencies."""

    class RgbColor(m.FrozenModel):
        """RGB or ARGB value with its optional tint."""

        kind: Literal["rgb"] = m.Field(default="rgb", description="Color kind.")
        value: Annotated[
            str,
            m.Field(
                pattern=r"^(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$",
                description="RGB or ARGB value.",
            ),
        ]
        tint: Annotated[float, m.Field(ge=-1, le=1, description="Color tint.")] = 0


__all__: list[str] = ["FlextCliModelsColor"]
