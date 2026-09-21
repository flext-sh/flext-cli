# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Typings package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .base import FlextCliTypesBase
    from .domain import FlextCliTypesDomain
    from .pipeline import FlextCliTypesPipeline
    from .xlsx import FlextCliTypesXlsx
__all__: tuple[str, ...] = (
    "FlextCliTypesBase", "FlextCliTypesDomain", "FlextCliTypesPipeline", "FlextCliTypesXlsx",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("FlextCliTypesBase",),
            ".domain": ("FlextCliTypesDomain",),
            ".pipeline": ("FlextCliTypesPipeline",),
            ".xlsx": ("FlextCliTypesXlsx",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
