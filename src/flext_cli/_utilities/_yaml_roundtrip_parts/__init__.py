# AUTO-GENERATED FILE — Regenerate with: make gen
"""Yaml Roundtrip Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._yaml_roundtrip_parts.flextcliutilitiesyamlroundtrip_part_02 import (
        FlextCliUtilitiesYamlRoundtrip as FlextCliUtilitiesYamlRoundtrip,
    )
_LAZY_IMPORTS = build_lazy_import_map({
    ".flextcliutilitiesyamlroundtrip_part_02": ("FlextCliUtilitiesYamlRoundtrip",)
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
