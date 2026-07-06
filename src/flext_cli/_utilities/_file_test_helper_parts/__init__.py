# AUTO-GENERATED FILE — Regenerate with: make gen
"""File Test Helper Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04 import (
        FlextCliUtilitiesFileTestHelpersMixin,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextcliutilitiesfiletesthelpersmixin_part_04": (
            "FlextCliUtilitiesFileTestHelpersMixin",
        ),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
