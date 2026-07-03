# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Toml Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_toml_utilities.testsflextclitomlutilities_part_03 import (
        TestsFlextCliTomlUtilities as TestsFlextCliTomlUtilities,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclitomlutilities_part_03": ("TestsFlextCliTomlUtilities",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
