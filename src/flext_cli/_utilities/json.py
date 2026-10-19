"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._json import FlextCliUtilitiesJsonNavigateMixin


class FlextCliUtilitiesJson(FlextCliUtilitiesJsonNavigateMixin):
    """Public facade for the generic JSON helpers behind ``u.Cli.json_*``."""


__all__: list[str] = ["FlextCliUtilitiesJson"]
