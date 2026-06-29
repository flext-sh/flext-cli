"""Behavioral tests for the prompts service."""

from __future__ import annotations

import importlib as _importlib

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


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_prompts.testsflextcliprompts_part_01"
    ),
    "TestsFlextCliPrompts",
    TestsFlextCliPrompts,
)
setattr(
    _importlib.import_module(
        "tests.unit._cases.test_prompts.testsflextcliprompts_part_02"
    ),
    "TestsFlextCliPrompts",
    TestsFlextCliPrompts,
)
