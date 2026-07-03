# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Examples Smoke package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_examples_smoke.testsflextcliexamplessmoke_part_05 import (
        TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmoke,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextcliexamplessmoke_part_05": ("TestsFlextCliExamplesSmoke",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
