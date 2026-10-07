"""Real Typer integration tests for the public flext-cli CLI facade.

Behavioral suite: every case exercises the public ``flext_cli.cli`` facade and
asserts observable contract only — command return values, Typer ``exit_code`` /
``stdout``, and ``r[T]`` outcomes (``tm.ok`` / ``tm.fail`` / ``result.error``).
No private attribute access, no mocking of internal collaborators.

The cases are split into MRO mixin parts under ``_cases`` purely for the
200-LOC module cap. They are aliased to non-``Test`` names here so pytest
collects them exactly once, through the single ``TestsFlextCliService`` facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.unit._cases.test_cli_service.testsflextcliservice_part_01 import (
    TestsFlextCliServicePart01,
)
from tests.unit._cases.test_cli_service.testsflextcliservice_part_02 import (
    TestsFlextCliServicePart02,
)
from tests.unit._cases.test_cli_service.testsflextcliservice_part_03 import (
    TestsFlextCliServicePart03,
)
from tests.unit._cases.test_cli_service.testsflextcliservice_part_04 import (
    TestsFlextCliServicePart04,
)
from tests.unit._cases.test_cli_service.testsflextcliservice_part_05 import (
    TestsFlextCliServicePart05,
)


class TestsFlextCliService(
    TestsFlextCliServicePart01,
    TestsFlextCliServicePart02,
    TestsFlextCliServicePart03,
    TestsFlextCliServicePart04,
    TestsFlextCliServicePart05,
):
    """Public behavioral suite for the flext-cli CLI facade."""
