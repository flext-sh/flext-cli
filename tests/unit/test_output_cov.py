"""Coverage tests for FlextCliUtilitiesOutput."""

from __future__ import annotations

import importlib as _importlib

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


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_output_cov.testsflextclioutputcov_part_01"
    ),
    "TestsFlextCliOutputCov",
    TestsFlextCliOutputCov,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_output_cov.testsflextclioutputcov_part_02"
    ),
    "TestsFlextCliOutputCov",
    TestsFlextCliOutputCov,
)
