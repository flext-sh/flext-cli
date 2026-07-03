# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Rules Cov package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_rules_cov.testsflextclirulescov_part_04 import (
        TestsFlextCliRulesCov as TestsFlextCliRulesCov,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclirulescov_part_04": ("TestsFlextCliRulesCov",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
