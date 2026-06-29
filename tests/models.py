"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.JsonValue
as data contracts. Reuse TestsFlextModels types where possible; add
test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib as _importlib

from flext_tests import FlextTestsModels

from flext_cli import m as flext_cli_m
from tests._models_parts.testsflextclimodels_part_01 import (
    TestsFlextCliModels as TestsFlextCliModelsPart01,
)


class TestsFlextCliModels(
    TestsFlextCliModelsPart01,
    FlextTestsModels,
    flext_cli_m,
):
    """Public facade for TestsFlextCliModels."""

    class Tests(TestsFlextCliModelsPart01.Tests):
        """Test-specific model namespace."""


m: type[TestsFlextCliModels] = TestsFlextCliModels

__all__: list[str] = ["TestsFlextCliModels", "m"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module("tests._models_parts.testsflextclimodels_part_01"),
    "TestsFlextCliModels",
    TestsFlextCliModels,
)
