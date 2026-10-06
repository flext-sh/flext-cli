# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples. Models Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

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

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ExamplesFlextCliModels": ".examplesflextclimodels_part_01",
        "ExamplesFlextCliModelsExamplesAdvanced": ".examples_advanced",
        "ExamplesFlextCliModelsExamplesCommon": ".examples_common",
        "ExamplesFlextCliModelsExamplesDatabase": ".examples_database",
    }),
    public_exports=__all__,
)
