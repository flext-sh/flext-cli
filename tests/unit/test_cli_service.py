"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

import importlib as _importlib

from ._cases.test_cli_service.testsflextcliservice_part_01 import (
    TestsFlextCliService as TestsFlextCliServicePart01,
)
from ._cases.test_cli_service.testsflextcliservice_part_02 import (
    TestsFlextCliService as TestsFlextCliServicePart02,
)
from ._cases.test_cli_service.testsflextcliservice_part_03 import (
    TestsFlextCliService as TestsFlextCliServicePart03,
)
from ._cases.test_cli_service.testsflextcliservice_part_04 import (
    TestsFlextCliService as TestsFlextCliServicePart04,
)
from ._cases.test_cli_service.testsflextcliservice_part_05 import (
    TestsFlextCliService as TestsFlextCliServicePart05,
)


class TestsFlextCliService(
    TestsFlextCliServicePart01,
    TestsFlextCliServicePart02,
    TestsFlextCliServicePart03,
    TestsFlextCliServicePart04,
    TestsFlextCliServicePart05,
):
    """Public facade for TestsFlextCliService."""


__all__: list[str] = ["TestsFlextCliService"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_cli_service.testsflextcliservice_part_01"
    ),
    "TestsFlextCliService",
    TestsFlextCliService,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_cli_service.testsflextcliservice_part_02"
    ),
    "TestsFlextCliService",
    TestsFlextCliService,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_cli_service.testsflextcliservice_part_03"
    ),
    "TestsFlextCliService",
    TestsFlextCliService,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_cli_service.testsflextcliservice_part_04"
    ),
    "TestsFlextCliService",
    TestsFlextCliService,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_cli_service.testsflextcliservice_part_05"
    ),
    "TestsFlextCliService",
    TestsFlextCliService,
)
