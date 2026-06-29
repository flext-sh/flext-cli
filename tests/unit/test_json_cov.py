"""Coverage tests for FlextCliUtilitiesJson."""

from __future__ import annotations

import importlib as _importlib

from ._cases.test_json_cov.testsflextclijsoncov_part_01 import (
    TestsFlextCliJsonCov as TestsFlextCliJsonCovPart01,
)
from ._cases.test_json_cov.testsflextclijsoncov_part_02 import (
    TestsFlextCliJsonCov as TestsFlextCliJsonCovPart02,
)


class TestsFlextCliJsonCov(
    TestsFlextCliJsonCovPart01,
    TestsFlextCliJsonCovPart02,
):
    """Public facade for TestsFlextCliJsonCov."""


__all__: list[str] = ["TestsFlextCliJsonCov"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_json_cov.testsflextclijsoncov_part_01"
    ),
    "TestsFlextCliJsonCov",
    TestsFlextCliJsonCov,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_json_cov.testsflextclijsoncov_part_02"
    ),
    "TestsFlextCliJsonCov",
    TestsFlextCliJsonCov,
)
