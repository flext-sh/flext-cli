"""Constants for flext-cli tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import c

from tests.constants_parts import (
    TestsFlextCliConstantsCore,
    TestsFlextCliConstantsRulesOptions,
    TestsFlextCliConstantsYamlOutput,
)


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
