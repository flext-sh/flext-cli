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

from examples.constants import ExamplesFlextCliConstants
from flext_tests import FlextTestsConstants

from flext_cli import FlextCliConstants
from tests._constants import TestsFlextCliConstantsPart01


class TestsFlextCliConstants(
    TestsFlextCliConstantsPart01,
    ExamplesFlextCliConstants,
    FlextTestsConstants,
    FlextCliConstants,
):
    """Public facade for TestsFlextCliConstants."""


c = TestsFlextCliConstants

__all__: list[str] = ["TestsFlextCliConstants", "c"]
