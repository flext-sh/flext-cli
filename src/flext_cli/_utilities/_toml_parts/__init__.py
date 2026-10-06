# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Toml Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_07 import (
        FlextCliUtilitiesToml,
    )


__all__: tuple[str, ...] = ("FlextCliUtilitiesToml",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextCliUtilitiesToml": ".flextcliutilitiestoml_part_07"}),
    public_exports=__all__,
)
