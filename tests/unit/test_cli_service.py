"""Real Typer integration tests for the public flext-cli CLI facade.

Behavioral suite: every case exercises the public ``flext_cli.cli`` facade and
asserts observable contract only — command return values, Typer ``exit_code`` /
``stdout``, and ``r[T]`` outcomes (``tm.ok`` / ``tm.fail`` / ``result.error``).
No private attribute access, no mocking of internal collaborators.

The cases are split into MRO mixin parts under ``_cases`` purely for the
200-LOC module cap. They are aliased to non-``Test`` names here so pytest
collects them exactly once, through the single ``TestsFlextCliService`` facade.
"""

from __future__ import annotations

from ._cases.test_cli_service.testsflextcliservice_part_01 import (
    TestsFlextCliService as _CliServicePart01,
)
from ._cases.test_cli_service.testsflextcliservice_part_02 import (
    TestsFlextCliService as _CliServicePart02,
)
from ._cases.test_cli_service.testsflextcliservice_part_03 import (
    TestsFlextCliService as _CliServicePart03,
)
from ._cases.test_cli_service.testsflextcliservice_part_04 import (
    TestsFlextCliService as _CliServicePart04,
)
from ._cases.test_cli_service.testsflextcliservice_part_05 import (
    TestsFlextCliService as _CliServicePart05,
)


class TestsFlextCliService(
    _CliServicePart01,
    _CliServicePart02,
    _CliServicePart03,
    _CliServicePart04,
    _CliServicePart05,
):
    """Public behavioral suite for the flext-cli CLI facade."""


__all__: list[str] = ["TestsFlextCliService"]
