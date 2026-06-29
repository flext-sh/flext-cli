"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

from ._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_01 import (
    TestsFlextCliPublicContractsCoverage as TestsFlextCliPublicContractsCoveragePart01,
)
from ._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_02 import (
    TestsFlextCliPublicContractsCoverage as TestsFlextCliPublicContractsCoveragePart02,
)
from ._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_03 import (
    TestsFlextCliPublicContractsCoverage as TestsFlextCliPublicContractsCoveragePart03,
)


class TestsFlextCliPublicContractsCoverage(
    TestsFlextCliPublicContractsCoveragePart01,
    TestsFlextCliPublicContractsCoveragePart02,
    TestsFlextCliPublicContractsCoveragePart03,
):
    """Public facade for TestsFlextCliPublicContractsCoverage."""


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
