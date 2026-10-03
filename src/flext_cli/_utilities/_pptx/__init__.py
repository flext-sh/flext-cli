# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Pptx package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._pptx._reader import FlextCliUtilitiesPptxReader
    from flext_cli._utilities._pptx._renderer import FlextCliUtilitiesPptxRenderer
    from flext_cli._utilities._pptx._serializer import FlextCliUtilitiesPptxSerializer


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesPptxReader",
    "FlextCliUtilitiesPptxRenderer",
    "FlextCliUtilitiesPptxSerializer",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._reader": ("FlextCliUtilitiesPptxReader",),
            "._renderer": ("FlextCliUtilitiesPptxRenderer",),
            "._serializer": ("FlextCliUtilitiesPptxSerializer",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
