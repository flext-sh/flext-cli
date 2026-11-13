# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Dag package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._dag.graph import FlextCliUtilitiesDagGraph
    from flext_cli._utilities._dag.waves import FlextCliUtilitiesDagWaves


__all__: tuple[str, ...] = ("FlextCliUtilitiesDagGraph", "FlextCliUtilitiesDagWaves")

install_lazy_exports(
    __name__,
    globals(),
    {"FlextCliUtilitiesDagGraph": ".graph", "FlextCliUtilitiesDagWaves": ".waves"},
    public_exports=__all__,
)
