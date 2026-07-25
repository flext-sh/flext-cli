"""User interaction tools for CLI applications."""

from __future__ import annotations

from flext_cli.services._prompts_parts.flextcliprompts_part_02 import (
    FlextCliPrompts as FlextCliPromptsPart02,
)


class FlextCliPrompts(FlextCliPromptsPart02):
    """Implementation part for FlextCliPrompts."""


__all__: list[str] = ["FlextCliPrompts"]
