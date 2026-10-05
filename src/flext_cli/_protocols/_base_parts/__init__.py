# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols. Base Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_05 import (
        FlextCliProtocolsBase,
    )


__all__: tuple[str, ...] = ("FlextCliProtocolsBase",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextCliProtocolsBase": ".flextcliprotocolsbase_part_05"}),
    public_exports=__all__,
)
