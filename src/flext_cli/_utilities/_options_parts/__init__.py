# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Options Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
    FlextCliUtilitiesOptionsPart02,
)


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesOptionBuilder": ".flextcliutilitiesoptionbuilder_part_01",
        "FlextCliUtilitiesOptions": ".flextcliutilitiesoptions_part_02",
    }),
    public_exports=__all__,
)
