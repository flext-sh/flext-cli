"""Constants for flext-cli tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import c

from tests._constants_parts.tests_core import TestsFlextCliConstantsCore
from tests._constants_parts.tests_rules_options import (
    TestsFlextCliConstantsRulesOptions,
)
from tests._constants_parts.tests_yaml_output import TestsFlextCliConstantsYamlOutput


class TestsFlextCliConstantsPart01:
    """Implementation part for TestsFlextCliConstantsPart01."""

    class Tests(
        TestsFlextCliConstantsCore,
        TestsFlextCliConstantsYamlOutput,
        TestsFlextCliConstantsRulesOptions,
        c.Tests,
    ):
        """Test-specific constant values for flext-cli."""


__all__: list[str] = ["TestsFlextCliConstantsPart01"]
