# AUTO-GENERATED FILE — Regenerate with: make gen
"""Files Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_04 import (
        FlextCliUtilitiesFiles as FlextCliUtilitiesFiles,
    )
_LAZY_IMPORTS = build_lazy_import_map({
    ".flextcliutilitiesfiles_part_04": ("FlextCliUtilitiesFiles",)
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
