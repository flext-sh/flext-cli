# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models. Base package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._models._base.flextclimodelsbase_part_10 import FlextCliModelsBase


__all__: tuple[str, ...] = ("FlextCliModelsBase",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextCliModelsBase": ".flextclimodelsbase_part_10"}),
    public_exports=__all__,
)
