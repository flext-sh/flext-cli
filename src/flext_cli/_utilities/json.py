"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities import FlextCliUtilitiesJsonNavigateMixin

# NOTE (multi-agent): mro-i6nq.13 — composed from the _json/{_navigate,_core}
# mixin chain (replacing the numbered _json_parts).


class FlextCliUtilitiesJson(FlextCliUtilitiesJsonNavigateMixin):
    """Public facade for the generic JSON helpers behind ``u.Cli.json_*``."""


__all__: list[str] = ["FlextCliUtilitiesJson"]
