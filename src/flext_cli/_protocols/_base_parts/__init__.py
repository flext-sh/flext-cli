# AUTO-GENERATED FILE — Regenerate with: make gen
"""Base Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_05 import (
        FlextCliProtocolsBase as FlextCliProtocolsBase,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextcliprotocolsbase_part_05": ("FlextCliProtocolsBase",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
