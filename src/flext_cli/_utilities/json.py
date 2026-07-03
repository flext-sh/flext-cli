"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.
"""

from __future__ import annotations

from flext_cli._utilities._json_parts.flextcliutilitiesjson_part_02 import (
    FlextCliUtilitiesJson as FlextCliUtilitiesJsonPart02,
)


class FlextCliUtilitiesJson(FlextCliUtilitiesJsonPart02):
    """Public facade for FlextCliUtilitiesJson."""


__all__: list[str] = ["FlextCliUtilitiesJson"]
