"""Coverage tests for _utilities/files.py — 100% via public interfaces."""

from __future__ import annotations

from ._cases.test_files_cov.testsflextclifilescov_part_01 import (
    TestsFlextCliFilesCov as TestsFlextCliFilesCovPart01,
)
from ._cases.test_files_cov.testsflextclifilescov_part_02 import (
    TestsFlextCliFilesCov as TestsFlextCliFilesCovPart02,
)


class TestsFlextCliFilesCov(
    TestsFlextCliFilesCovPart01,
    TestsFlextCliFilesCovPart02,
):
    """Public facade for TestsFlextCliFilesCov."""


__all__: list[str] = ["TestsFlextCliFilesCov"]
