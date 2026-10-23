"""Behavioral tests for the prompts service.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from tests import c, p, tm

if TYPE_CHECKING:
    from collections.abc import Callable


class TestsFlextCliPromptsPart02:
    """Implementation part for TestsFlextCliPromptsPart02."""

    @staticmethod
    @pytest.mark.parametrize("message", c.Tests.PROMPT_EDGE_MESSAGES)
    def test_prompt_accepts_edge_case_messages(
        make_prompts: Callable[..., p.Tests.Prompts],
        message: str,
    ) -> None:
        """Verify that prompt accepts edge case messages."""
        prompts = make_prompts(interactive_mode=False)
        result = prompts.prompt(message, default="text")
        tm.ok(result, eq="text")

    @staticmethod
    def test_repeated_prompt_operations_remain_fast(
        make_prompts: Callable[..., p.Tests.Prompts],
    ) -> None:
        """Verify that repeated prompt operations remain fast."""
        prompts = make_prompts(interactive_mode=False)
        started_at = time.time()
        for index in range(100):
            result = prompts.prompt(f"Prompt {index}", default="text")
            tm.ok(result, eq="text")
        tm.that(time.time() - started_at, lt=0.5)
