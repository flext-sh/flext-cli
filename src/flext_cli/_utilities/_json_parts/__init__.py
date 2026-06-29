# AUTO-GENERATED FILE — Regenerate with: make gen
"""Json Parts package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_cli._utilities._json_parts.flextcliutilitiesjson_part_03 import (
        FlextCliUtilitiesJson as FlextCliUtilitiesJson,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextcliutilitiesjson_part_03": ("FlextCliUtilitiesJson",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
