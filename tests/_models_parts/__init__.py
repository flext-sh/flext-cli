# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Models Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from tests._models_parts.tests_cli import TestsFlextCliModelsCli
    from tests._models_parts.tests_runtime import TestsFlextCliModelsRuntime
    from tests._models_parts.testsflextclimodels_part_01 import (
        TestsFlextCliModelsPart01,
    )


__all__: tuple[str, ...] = (
    "TestsFlextCliModelsCli",
    "TestsFlextCliModelsPart01",
    "TestsFlextCliModelsRuntime",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextCliModelsCli": ".tests_cli",
        "TestsFlextCliModelsPart01": ".testsflextclimodels_part_01",
        "TestsFlextCliModelsRuntime": ".tests_runtime",
    }),
    public_exports=__all__,
)
