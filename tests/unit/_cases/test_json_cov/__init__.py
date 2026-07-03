# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Json Cov package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_json_cov.testsflextclijsoncov_part_02 import (
        TestsFlextCliJsonCov as TestsFlextCliJsonCov,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclijsoncov_part_02": ("TestsFlextCliJsonCov",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
