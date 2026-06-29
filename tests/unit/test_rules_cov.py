"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

import importlib as _importlib

from ._cases.test_rules_cov.testsflextclirulescov_part_01 import (
    TestsFlextCliRulesCov as TestsFlextCliRulesCovPart01,
)
from ._cases.test_rules_cov.testsflextclirulescov_part_02 import (
    TestsFlextCliRulesCov as TestsFlextCliRulesCovPart02,
)
from ._cases.test_rules_cov.testsflextclirulescov_part_03 import (
    TestsFlextCliRulesCov as TestsFlextCliRulesCovPart03,
)
from ._cases.test_rules_cov.testsflextclirulescov_part_04 import (
    TestsFlextCliRulesCov as TestsFlextCliRulesCovPart04,
)


class TestsFlextCliRulesCov(
    TestsFlextCliRulesCovPart01,
    TestsFlextCliRulesCovPart02,
    TestsFlextCliRulesCovPart03,
    TestsFlextCliRulesCovPart04,
):
    """Public facade for TestsFlextCliRulesCov."""


__all__: list[str] = ["TestsFlextCliRulesCov"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_rules_cov.testsflextclirulescov_part_01"
    ),
    "TestsFlextCliRulesCov",
    TestsFlextCliRulesCov,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_rules_cov.testsflextclirulescov_part_02"
    ),
    "TestsFlextCliRulesCov",
    TestsFlextCliRulesCov,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_rules_cov.testsflextclirulescov_part_03"
    ),
    "TestsFlextCliRulesCov",
    TestsFlextCliRulesCov,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_rules_cov.testsflextclirulescov_part_04"
    ),
    "TestsFlextCliRulesCov",
    TestsFlextCliRulesCov,
)
