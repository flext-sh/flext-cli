# AUTO-GENERATED FILE — Regenerate with: make gen
"""Options Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder as FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions as FlextCliUtilitiesOptions,
    )
_LAZY_IMPORTS = build_lazy_import_map({
    ".flextcliutilitiesoptionbuilder_part_01": ("FlextCliUtilitiesOptionBuilder",),
    ".flextcliutilitiesoptions_part_02": ("FlextCliUtilitiesOptions",),
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
