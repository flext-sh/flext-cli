# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services. Cli Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services._cli_parts.flextclicli_part_06 import FlextCliCliPart06


__all__: tuple[str, ...] = ("FlextCliCli",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextCliCli": ".flextclicli_part_06"}),
    public_exports=__all__,
)
