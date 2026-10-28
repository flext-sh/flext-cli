"""Extracted facade class for pptx.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._pptx import (
    FlextCliUtilitiesPptxReader,
    FlextCliUtilitiesPptxRenderer,
    FlextCliUtilitiesPptxSerializer,
)


class FlextCliUtilitiesPptx(
    FlextCliUtilitiesPptxReader,
    FlextCliUtilitiesPptxRenderer,
    FlextCliUtilitiesPptxSerializer,
):
    """Facade for pptx."""


__all__: list[str] = ["FlextCliUtilitiesPptx"]
