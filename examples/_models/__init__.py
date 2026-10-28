# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples._models.examples_advanced import (
        ExamplesFlextCliModelsExamplesAdvanced,
    )
    from examples._models.examples_common import ExamplesFlextCliModelsExamplesCommon
    from examples._models.examples_database import (
        ExamplesFlextCliModelsExamplesDatabase,
    )
    from examples._models.examplesflextclimodels_part_01 import (
        ExamplesFlextCliModelsPart01,
    )


__all__: tuple[str, ...] = (
    "ExamplesFlextCliModelsExamplesAdvanced",
    "ExamplesFlextCliModelsExamplesCommon",
    "ExamplesFlextCliModelsExamplesDatabase",
    "ExamplesFlextCliModelsPart01",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ExamplesFlextCliModelsExamplesAdvanced": ".examples_advanced",
        "ExamplesFlextCliModelsExamplesCommon": ".examples_common",
        "ExamplesFlextCliModelsExamplesDatabase": ".examples_database",
        "ExamplesFlextCliModelsPart01": ".examplesflextclimodels_part_01",
    }),
    public_exports=__all__,
)
