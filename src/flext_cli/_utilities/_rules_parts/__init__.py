# AUTO-GENERATED FILE — Regenerate with: make gen
"""Rules Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_03 import (
        FlextCliUtilitiesRules as FlextCliUtilitiesRules,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextcliutilitiesrules_part_03": ("FlextCliUtilitiesRules",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
