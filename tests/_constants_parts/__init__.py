# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Constants Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".tests_core": ("TestsFlextCliConstantsCore",),
            ".tests_rules_options": ("TestsFlextCliConstantsRulesOptions",),
            ".tests_yaml_output": ("TestsFlextCliConstantsYamlOutput",),
            ".testsflextcliconstants_part_01": ("TestsFlextCliConstants",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
