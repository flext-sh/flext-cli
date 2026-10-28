# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for json.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._json.core import FlextCliUtilitiesJsonCore
    from flext_cli._utilities._json.navigate import FlextCliUtilitiesJsonNavigate

__all__: tuple[str, ...] = (
    "FlextCliUtilitiesJsonCore",
    "FlextCliUtilitiesJsonNavigate",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesJsonCore": ".core",
        "FlextCliUtilitiesJsonNavigate": ".navigate",
    }),
    public_exports=__all__,
)
