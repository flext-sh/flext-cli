"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

from ._cases.test_toml_utilities.testsflextclitomlutilities_part_01 import (
    TestsFlextCliTomlUtilities as TestsFlextCliTomlUtilitiesPart01,
)
from ._cases.test_toml_utilities.testsflextclitomlutilities_part_02 import (
    TestsFlextCliTomlUtilities as TestsFlextCliTomlUtilitiesPart02,
)
from ._cases.test_toml_utilities.testsflextclitomlutilities_part_03 import (
    TestsFlextCliTomlUtilities as TestsFlextCliTomlUtilitiesPart03,
)


class TestsFlextCliTomlUtilities(
    TestsFlextCliTomlUtilitiesPart01,
    TestsFlextCliTomlUtilitiesPart02,
    TestsFlextCliTomlUtilitiesPart03,
):
    """Public facade for TestsFlextCliTomlUtilities."""


__all__: list[str] = ["TestsFlextCliTomlUtilities"]
