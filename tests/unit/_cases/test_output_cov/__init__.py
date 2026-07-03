# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Output Cov package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_output_cov.testsflextclioutputcov_part_02 import (
        TestsFlextCliOutputCov as TestsFlextCliOutputCov,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclioutputcov_part_02": ("TestsFlextCliOutputCov",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
