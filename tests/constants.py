# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants for flext-cli tests.

Provides TestsFlextCliConstants, extending FlextTestsConstants with flext-cli-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- FlextTestsConstants (flext_tests) - Provides .Tests.* namespace
- c (production) - Provides .Cli.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from examples import c as examples_c
from flext_tests import c as flext_tests_c

from tests._constants import (
    TestsFlextCliConstantsCore,
    TestsFlextCliConstantsPart01,
    TestsFlextCliConstantsRulesOptions,
    TestsFlextCliConstantsYamlOutput,
)


class TestsFlextCliConstants(
    TestsFlextCliConstantsPart01,
    TestsFlextCliConstantsCore,
    TestsFlextCliConstantsRulesOptions,
    TestsFlextCliConstantsYamlOutput,
    flext_tests_c,
    examples_c,
):
    """Public facade for TestsFlextCliConstants."""


c = TestsFlextCliConstants
__all__: list[str] = ["TestsFlextCliConstants", "c"]
