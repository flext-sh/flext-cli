# AUTO-GENERATED FILE — Regenerate with: make gen
"""Typings package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._typings.base import FlextCliTypesBase as FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain as FlextCliTypesDomain
    from flext_cli._typings.pipeline import (
        FlextCliTypesPipeline as FlextCliTypesPipeline,
    )
_LAZY_IMPORTS = build_lazy_import_map({
    ".base": ("FlextCliTypesBase",),
    ".domain": ("FlextCliTypesDomain",),
    ".pipeline": ("FlextCliTypesPipeline",),
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
