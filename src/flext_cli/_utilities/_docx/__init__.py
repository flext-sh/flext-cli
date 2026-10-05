# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Docx package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._docx._reader import FlextCliUtilitiesDocxReader
    from flext_cli._utilities._docx._renderer import FlextCliUtilitiesDocxRenderer


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesDocxReader",
    "FlextCliUtilitiesDocxRenderer",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesDocxReader": "._reader",
        "FlextCliUtilitiesDocxRenderer": "._renderer",
    }),
    public_exports=__all__,
)
