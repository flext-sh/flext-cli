"""User interaction tools for CLI applications."""

from __future__ import annotations

from flext_cli.services._prompts_parts.flextcliprompts_part_03 import (
    FlextCliPrompts as FlextCliPromptsPart03,
)


class FlextCliPrompts(FlextCliPromptsPart03):
    """Public facade for FlextCliPrompts."""


__all__: list[str] = ["FlextCliPrompts"]
