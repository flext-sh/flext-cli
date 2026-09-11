"""Pydantic models for flext-cli tests only."""

from __future__ import annotations

from flext_tests import m

from .tests_cli import TestsFlextCliModelsCli
from .tests_runtime import TestsFlextCliModelsRuntime


class TestsFlextCliModels:
    """Implementation part for TestsFlextCliModels."""

    class Tests(TestsFlextCliModelsRuntime, TestsFlextCliModelsCli, m.Tests):
        """Test-specific model definitions for flext-cli."""


__all__: list[str] = ["TestsFlextCliModels"]
