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

from flext_tests import FlextTestsConstants

from flext_cli import c as flext_cli_c
from tests._constants_parts.testsflextcliconstants_part_01 import (
    TestsFlextCliConstants as TestsFlextCliConstantsPart01,
)


class TestsFlextCliConstants(
    TestsFlextCliConstantsPart01, FlextTestsConstants, flext_cli_c
):
    """Public facade for TestsFlextCliConstants."""


c: type[TestsFlextCliConstants] = TestsFlextCliConstants

__all__: list[str] = ["TestsFlextCliConstants", "c"]
