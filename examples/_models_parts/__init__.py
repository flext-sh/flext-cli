# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples. Models Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from examples._models_parts.examples_advanced import (
        ExamplesFlextCliModelsExamplesAdvanced,
    )
    from examples._models_parts.examples_common import (
        ExamplesFlextCliModelsExamplesCommon,
    )
    from examples._models_parts.examples_database import (
        ExamplesFlextCliModelsExamplesDatabase,
    )
    from examples._models_parts.examplesflextclimodels_part_01 import (
        ExamplesFlextCliModels,
    )


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
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
