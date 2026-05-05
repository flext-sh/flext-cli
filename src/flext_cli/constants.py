"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

from flext_cli import (
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsExceptions,
    FlextCliConstantsOutput,
    FlextCliConstantsPipeline,
    FlextCliConstantsSettings,
)
from flext_core import FlextConstants


class FlextCliConstants(
    FlextConstants,
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsExceptions,
    FlextCliConstantsOutput,
    FlextCliConstantsPipeline,
    FlextCliConstantsSettings,
):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsPipeline,
        FlextCliConstantsBase,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        FlextCliConstantsExceptions,
        FlextCliConstantsOutput,
        FlextCliConstantsSettings,
    ):
        """CLI related constants."""


__all__: tuple[str, ...] = ("FlextCliConstants", "c")

c = FlextCliConstants
