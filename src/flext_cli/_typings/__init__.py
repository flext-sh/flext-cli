# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._typings.base import FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain
    from flext_cli._typings.pipeline import FlextCliTypesPipeline
    from flext_cli._typings.xlsx import FlextCliTypesXlsx


__all__: tuple[str, ...] = (
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "FlextCliTypesPipeline",
    "FlextCliTypesXlsx",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("FlextCliTypesBase",),
            ".domain": ("FlextCliTypesDomain",),
            ".pipeline": ("FlextCliTypesPipeline",),
            ".xlsx": ("FlextCliTypesXlsx",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
