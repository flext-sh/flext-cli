# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Docx package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._docx.formatting import FlextCliUtilitiesDocxFormatting
    from flext_cli._utilities._docx.reader import FlextCliUtilitiesDocxReader
    from flext_cli._utilities._docx.renderer import FlextCliUtilitiesDocxRenderer


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesDocxFormatting",
    "FlextCliUtilitiesDocxReader",
    "FlextCliUtilitiesDocxRenderer",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliUtilitiesDocxFormatting": ".formatting",
        "FlextCliUtilitiesDocxReader": ".reader",
        "FlextCliUtilitiesDocxRenderer": ".renderer",
    },
    public_exports=__all__,
)
