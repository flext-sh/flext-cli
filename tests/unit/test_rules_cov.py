"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

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
