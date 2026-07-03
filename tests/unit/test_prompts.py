"""Behavioral tests for the prompts service."""

from __future__ import annotations

from ._cases.test_prompts.testsflextcliprompts_part_01 import (
    TestsFlextCliPrompts as TestsFlextCliPromptsPart01,
)
from ._cases.test_prompts.testsflextcliprompts_part_02 import (
    TestsFlextCliPrompts as TestsFlextCliPromptsPart02,
)


class TestsFlextCliPrompts(
    TestsFlextCliPromptsPart01,
    TestsFlextCliPromptsPart02,
):
    """Public facade for TestsFlextCliPrompts."""


__all__: list[str] = ["TestsFlextCliPrompts"]
