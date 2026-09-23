# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Models Parts package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .tests_cli import TestsFlextCliModelsCli
    from .tests_runtime import TestsFlextCliModelsRuntime
    from .testsflextclimodels_part_01 import TestsFlextCliModels


__all__: tuple[str, ...] = (
    "TestsFlextCliModels",
    "TestsFlextCliModelsCli",
    "TestsFlextCliModelsRuntime",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".tests_cli": ("TestsFlextCliModelsCli",),
            ".tests_runtime": ("TestsFlextCliModelsRuntime",),
            ".testsflextclimodels_part_01": ("TestsFlextCliModels",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
