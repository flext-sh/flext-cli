"""Pydantic models for flext-cli tests only.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import m

from tests._models_parts.tests_cli import TestsFlextCliModelsCli
from tests._models_parts.tests_runtime import TestsFlextCliModelsRuntime


class TestsFlextCliModelsPart01:
    """Implementation part for TestsFlextCliModelsPart01."""

    class Tests(TestsFlextCliModelsRuntime, TestsFlextCliModelsCli, m.Tests):
        """Test-specific model definitions for flext-cli."""


__all__: list[str] = ["TestsFlextCliModelsPart01"]
