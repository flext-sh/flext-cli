# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for pptx.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._pptx.reader import FlextCliUtilitiesPptxReader
    from flext_cli._utilities._pptx.renderer import FlextCliUtilitiesPptxRenderer
    from flext_cli._utilities._pptx.serializer import FlextCliUtilitiesPptxSerializer

__all__: tuple[str, ...] = (
    "FlextCliUtilitiesPptxReader",
    "FlextCliUtilitiesPptxRenderer",
    "FlextCliUtilitiesPptxSerializer",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesPptxReader": ".reader",
        "FlextCliUtilitiesPptxRenderer": ".renderer",
        "FlextCliUtilitiesPptxSerializer": ".serializer",
    }),
    public_exports=__all__,
)
