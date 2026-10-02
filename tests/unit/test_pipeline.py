"""Unit tests for the DAG pipeline engine.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.unit._cases.test_pipeline.testsflextclipipeline_part_01 import (
    TestsFlextCliPipeline as TestsFlextCliPipelinePart01,
)
from tests.unit._cases.test_pipeline.testsflextclipipeline_part_02 import (
    TestsFlextCliPipeline as TestsFlextCliPipelinePart02,
)
from tests.unit._cases.test_pipeline.testsflextclipipeline_part_03 import (
    TestsFlextCliPipeline as TestsFlextCliPipelinePart03,
)


class TestsFlextCliPipeline(
    TestsFlextCliPipelinePart01,
    TestsFlextCliPipelinePart02,
    TestsFlextCliPipelinePart03,
):
    """Public facade for TestsFlextCliPipeline."""
