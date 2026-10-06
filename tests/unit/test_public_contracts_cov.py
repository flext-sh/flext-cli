"""Public contract coverage tests for the flext-cli facade and models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_01 import (
    TestsFlextCliPublicContractsCoveragePart01,
)
from tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_02 import (
    TestsFlextCliPublicContractsCoveragePart02,
)
from tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_03 import (
    TestsFlextCliPublicContractsCoveragePart03,
)


class TestsFlextCliPublicContractsCoverage(
    TestsFlextCliPublicContractsCoveragePart01,
    TestsFlextCliPublicContractsCoveragePart02,
    TestsFlextCliPublicContractsCoveragePart03,
):
    """Public facade for TestsFlextCliPublicContractsCoverage."""
