# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Options Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".flextcliutilitiesoptionbuilder_part_01": (
                "FlextCliUtilitiesOptionBuilder",
            ),
            ".flextcliutilitiesoptions_part_02": ("FlextCliUtilitiesOptions",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
