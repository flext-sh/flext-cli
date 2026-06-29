"""Constants for flext-cli tests."""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from tests._constants_parts.tests_core import TestsFlextCliConstantsCore
from tests._constants_parts.tests_rules_options import (
    TestsFlextCliConstantsRulesOptions,
)
from tests._constants_parts.tests_yaml_output import TestsFlextCliConstantsYamlOutput


class TestsFlextCliConstants:
    """Implementation part for TestsFlextCliConstants."""

    class Tests(
        TestsFlextCliConstantsCore,
        TestsFlextCliConstantsYamlOutput,
        TestsFlextCliConstantsRulesOptions,
        FlextTestsConstants.Tests,
    ):
        """Test-specific constant values for flext-cli."""


__all__: list[str] = ["TestsFlextCliConstants"]
