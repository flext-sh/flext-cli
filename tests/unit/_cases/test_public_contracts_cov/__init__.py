# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit. Cases.test Public Contracts Cov package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .testsflextclipubliccontractscoverage_part_03 import (
        TestsFlextCliPublicContractsCoverage,
    )
__all__: tuple[str, ...] = ("TestsFlextCliPublicContractsCoverage",)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".testsflextclipubliccontractscoverage_part_03": (
                "TestsFlextCliPublicContractsCoverage",
            )
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
