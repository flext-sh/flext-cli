# AUTO-GENERATED FILE — Regenerate with: make gen
"""Toml Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_07 import (
        FlextCliUtilitiesToml as FlextCliUtilitiesToml,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextcliutilitiestoml_part_07": ("FlextCliUtilitiesToml",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
