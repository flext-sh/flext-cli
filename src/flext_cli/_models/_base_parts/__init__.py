# AUTO-GENERATED FILE — Regenerate with: make gen
"""Base Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._models._base_parts.flextclimodelsbase_part_07 import (
        FlextCliModelsBase as FlextCliModelsBase,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextclimodelsbase_part_07": ("FlextCliModelsBase",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
