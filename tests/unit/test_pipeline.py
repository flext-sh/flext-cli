"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

import importlib as _importlib

from ._cases.test_pipeline.testsflextclipipeline_part_01 import (
    TestsFlextCliPipeline as TestsFlextCliPipelinePart01,
)
from ._cases.test_pipeline.testsflextclipipeline_part_02 import (
    TestsFlextCliPipeline as TestsFlextCliPipelinePart02,
)
from ._cases.test_pipeline.testsflextclipipeline_part_03 import (
    TestsFlextCliPipeline as TestsFlextCliPipelinePart03,
)


class TestsFlextCliPipeline(
    TestsFlextCliPipelinePart01,
    TestsFlextCliPipelinePart02,
    TestsFlextCliPipelinePart03,
):
    """Public facade for TestsFlextCliPipeline."""


__all__: list[str] = ["TestsFlextCliPipeline"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_pipeline.testsflextclipipeline_part_01"
    ),
    "TestsFlextCliPipeline",
    TestsFlextCliPipeline,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_pipeline.testsflextclipipeline_part_02"
    ),
    "TestsFlextCliPipeline",
    TestsFlextCliPipeline,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_pipeline.testsflextclipipeline_part_03"
    ),
    "TestsFlextCliPipeline",
    TestsFlextCliPipeline,
)
