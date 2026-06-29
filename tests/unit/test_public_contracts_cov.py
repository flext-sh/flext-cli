"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

import importlib as _importlib

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


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_01"
    ),
    "TestsFlextCliPublicContractsCoverage",
    TestsFlextCliPublicContractsCoverage,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_02"
    ),
    "TestsFlextCliPublicContractsCoverage",
    TestsFlextCliPublicContractsCoverage,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_public_contracts_cov.testsflextclipubliccontractscoverage_part_03"
    ),
    "TestsFlextCliPublicContractsCoverage",
    TestsFlextCliPublicContractsCoverage,
)
