# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT CLI utility facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextUtilities

from flext_cli._utilities import FlextCliUtilitiesCli


class FlextCliUtilities(FlextUtilities):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(FlextCliUtilitiesCli):
        """CLI utility namespace."""


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "FlextCliUtilitiesCli", "u"]
