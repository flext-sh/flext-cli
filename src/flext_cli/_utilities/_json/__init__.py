# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Json package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._json._core import FlextCliUtilitiesJsonCoreMixin
    from flext_cli._utilities._json._navigate import FlextCliUtilitiesJsonNavigateMixin


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesJsonCoreMixin",
    "FlextCliUtilitiesJsonNavigateMixin",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesJsonCoreMixin": "._core",
        "FlextCliUtilitiesJsonNavigateMixin": "._navigate",
    }),
    public_exports=__all__,
)
