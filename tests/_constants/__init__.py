# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests._constants.tests_core import TestsFlextCliConstantsCore
    from tests._constants.tests_rules_options import TestsFlextCliConstantsRulesOptions
    from tests._constants.tests_yaml_output import TestsFlextCliConstantsYamlOutput
    from tests._constants.testsflextcliconstants_part_01 import (
        TestsFlextCliConstantsPart01,
    )


__all__: tuple[str, ...] = (
    "TestsFlextCliConstantsCore",
    "TestsFlextCliConstantsPart01",
    "TestsFlextCliConstantsRulesOptions",
    "TestsFlextCliConstantsYamlOutput",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextCliConstantsCore": ".tests_core",
        "TestsFlextCliConstantsPart01": ".testsflextcliconstants_part_01",
        "TestsFlextCliConstantsRulesOptions": ".tests_rules_options",
        "TestsFlextCliConstantsYamlOutput": ".tests_yaml_output",
    }),
    public_exports=__all__,
)
