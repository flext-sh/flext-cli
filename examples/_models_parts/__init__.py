# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples. Models Parts package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .examples_advanced import ExamplesFlextCliModelsExamplesAdvanced
    from .examples_common import ExamplesFlextCliModelsExamplesCommon
    from .examples_database import ExamplesFlextCliModelsExamplesDatabase
    from .examplesflextclimodels_part_01 import ExamplesFlextCliModels
__all__: tuple[str, ...] = (
    "ExamplesFlextCliModels",
    "ExamplesFlextCliModelsExamplesAdvanced",
    "ExamplesFlextCliModelsExamplesCommon",
    "ExamplesFlextCliModelsExamplesDatabase",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".examples_advanced": ("ExamplesFlextCliModelsExamplesAdvanced",),
            ".examples_common": ("ExamplesFlextCliModelsExamplesCommon",),
            ".examples_database": ("ExamplesFlextCliModelsExamplesDatabase",),
            ".examplesflextclimodels_part_01": ("ExamplesFlextCliModels",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
