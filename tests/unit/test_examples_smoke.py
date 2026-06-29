"""Smoke tests for flext-cli examples using the public cli facade."""

from __future__ import annotations

from ._cases.test_examples_smoke.testsflextcliexamplessmoke_part_01 import (
    TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmokePart01,
)
from ._cases.test_examples_smoke.testsflextcliexamplessmoke_part_02 import (
    TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmokePart02,
)
from ._cases.test_examples_smoke.testsflextcliexamplessmoke_part_03 import (
    TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmokePart03,
)
from ._cases.test_examples_smoke.testsflextcliexamplessmoke_part_04 import (
    TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmokePart04,
)
from ._cases.test_examples_smoke.testsflextcliexamplessmoke_part_05 import (
    TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmokePart05,
)


class TestsFlextCliExamplesSmoke(
    TestsFlextCliExamplesSmokePart01,
    TestsFlextCliExamplesSmokePart02,
    TestsFlextCliExamplesSmokePart03,
    TestsFlextCliExamplesSmokePart04,
    TestsFlextCliExamplesSmokePart05,
):
    """Public facade for TestsFlextCliExamplesSmoke."""


__all__: list[str] = ["TestsFlextCliExamplesSmoke"]
