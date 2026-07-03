# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Public Contracts Cov package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_03 import (
        TestsFlextCliPublicContractsCoverage as TestsFlextCliPublicContractsCoverage,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclipubliccontractscoverage_part_03": (
            "TestsFlextCliPublicContractsCoverage",
        ),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
