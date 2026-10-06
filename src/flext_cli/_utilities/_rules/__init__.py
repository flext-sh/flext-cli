# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Rules package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._rules._loaders import FlextCliUtilitiesRulesLoadersMixin
    from flext_cli._utilities._rules._matchers import (
        FlextCliUtilitiesRulesMatchersMixin,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesRulesLoadersMixin",
    "FlextCliUtilitiesRulesMatchersMixin",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesRulesLoadersMixin": "._loaders",
        "FlextCliUtilitiesRulesMatchersMixin": "._matchers",
    }),
    public_exports=__all__,
)
