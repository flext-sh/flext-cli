# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Constants Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from tests._constants_parts.tests_core import TestsFlextCliConstantsCore
    from tests._constants_parts.tests_rules_options import (
        TestsFlextCliConstantsRulesOptions,
    )
    from tests._constants_parts.tests_yaml_output import (
        TestsFlextCliConstantsYamlOutput,
    )
    from tests._constants_parts.testsflextcliconstants_part_01 import (
        TestsFlextCliConstants,
    )


__all__: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliConstantsCore",
    "TestsFlextCliConstantsRulesOptions",
    "TestsFlextCliConstantsYamlOutput",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextCliConstants": ".testsflextcliconstants_part_01",
        "TestsFlextCliConstantsCore": ".tests_core",
        "TestsFlextCliConstantsRulesOptions": ".tests_rules_options",
        "TestsFlextCliConstantsYamlOutput": ".tests_yaml_output",
    }),
    public_exports=__all__,
)
