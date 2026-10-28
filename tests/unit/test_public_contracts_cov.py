"""Public contract coverage tests for the flext-cli facade and models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from tests.unit.cases.test_public_contracts_cov import (
    testsflextclipubliccontractscoverage_part_01 as settings_contracts,
    testsflextclipubliccontractscoverage_part_02 as model_contracts,
    testsflextclipubliccontractscoverage_part_03 as pipeline_contracts,
)


class TestsFlextCliPublicContractsCoverage(
    settings_contracts.TestsFlextCliPublicContractsCoveragePart01,
    model_contracts.TestsFlextCliPublicContractsCoveragePart02,
    pipeline_contracts.TestsFlextCliPublicContractsCoveragePart03,
):
    """Public facade for TestsFlextCliPublicContractsCoverage."""
