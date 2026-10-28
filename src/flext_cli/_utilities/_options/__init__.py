# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Options package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._options.annotations import (
        FlextCliUtilitiesOptionsAnnotations,
    )
    from flext_cli._utilities._options.fields import FlextCliUtilitiesOptionsFields
    from flext_cli._utilities._options.option_builder import (
        FlextCliUtilitiesOptionBuilder,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptionsAnnotations",
    "FlextCliUtilitiesOptionsFields",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesOptionBuilder": ".option_builder",
        "FlextCliUtilitiesOptionsAnnotations": ".annotations",
        "FlextCliUtilitiesOptionsFields": ".fields",
    }),
    public_exports=__all__,
)
