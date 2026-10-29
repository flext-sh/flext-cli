"""Extracted facade class for docx.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._docx import (
    FlextCliUtilitiesDocxReader,
    FlextCliUtilitiesDocxRenderer,
)


class FlextCliUtilitiesDocx(
    FlextCliUtilitiesDocxReader,
    FlextCliUtilitiesDocxRenderer,
):
    """Facade for docx."""


__all__: list[str] = ["FlextCliUtilitiesDocx"]
