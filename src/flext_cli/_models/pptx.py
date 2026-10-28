"""Private MRO composition for generic PPTX models.

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

from flext_cli._models import FlextCliModelsPptxPresentation


class FlextCliModelsPptx(FlextCliModelsPptxPresentation):
    """Canonical private PPTX model namespace."""


__all__: tuple[str, ...] = ("FlextCliModelsPptx",)
