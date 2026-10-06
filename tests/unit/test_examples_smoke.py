"""Smoke tests for flext-cli examples using the public cli facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.unit._cases.test_examples_smoke.testsflextcliexamplessmoke_part_01 import (
    TestsFlextCliExamplesSmokePart01,
)
from tests.unit._cases.test_examples_smoke.testsflextcliexamplessmoke_part_02 import (
    TestsFlextCliExamplesSmokePart02,
)
from tests.unit._cases.test_examples_smoke.testsflextcliexamplessmoke_part_03 import (
    TestsFlextCliExamplesSmokePart03,
)
from tests.unit._cases.test_examples_smoke.testsflextcliexamplessmoke_part_04 import (
    TestsFlextCliExamplesSmokePart04,
)
from tests.unit._cases.test_examples_smoke.testsflextcliexamplessmoke_part_05 import (
    TestsFlextCliExamplesSmokePart05,
)


class TestsFlextCliExamplesSmoke(
    TestsFlextCliExamplesSmokePart01,
    TestsFlextCliExamplesSmokePart02,
    TestsFlextCliExamplesSmokePart03,
    TestsFlextCliExamplesSmokePart04,
    TestsFlextCliExamplesSmokePart05,
):
    """Public facade for TestsFlextCliExamplesSmoke."""
