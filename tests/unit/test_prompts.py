"""Behavioral tests for the prompts service.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.unit._cases.test_prompts.testsflextcliprompts_part_01 import (
    TestsFlextCliPromptsPart01,
)
from tests.unit._cases.test_prompts.testsflextcliprompts_part_02 import (
    TestsFlextCliPromptsPart02,
)


class TestsFlextCliPrompts(TestsFlextCliPromptsPart01, TestsFlextCliPromptsPart02):
    """Public facade for TestsFlextCliPrompts."""
