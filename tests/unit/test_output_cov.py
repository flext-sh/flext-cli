"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

from ._cases.test_output_cov.testsflextclioutputcov_part_01 import (
    TestsFlextCliOutputCov as TestsFlextCliOutputCovPart01,
)
from ._cases.test_output_cov.testsflextclioutputcov_part_02 import (
    TestsFlextCliOutputCov as TestsFlextCliOutputCovPart02,
)


class TestsFlextCliOutputCov(
    TestsFlextCliOutputCovPart01,
    TestsFlextCliOutputCovPart02,
):
    """Public facade for TestsFlextCliOutputCov."""


__all__: list[str] = ["TestsFlextCliOutputCov"]
