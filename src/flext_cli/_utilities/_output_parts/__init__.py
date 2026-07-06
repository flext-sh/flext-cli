# AUTO-GENERATED FILE — Regenerate with: make gen
"""Output Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._output_parts.flextcliutilitiesoutput_part_02 import (
        FlextCliUtilitiesOutput,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextcliutilitiesoutput_part_02": ("FlextCliUtilitiesOutput",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
