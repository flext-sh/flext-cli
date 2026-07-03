# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Pipeline package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_pipeline.testsflextclipipeline_part_03 import (
        TestsFlextCliPipeline as TestsFlextCliPipeline,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclipipeline_part_03": ("TestsFlextCliPipeline",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
