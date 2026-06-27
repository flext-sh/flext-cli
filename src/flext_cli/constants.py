"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

from flext_cli import (
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsExceptions,
    FlextCliConstantsFiles,
    FlextCliConstantsOutput,
    FlextCliConstantsPipeline,
    FlextCliConstantsSettings,
)
from flext_core import FlextConstants, t


class FlextCliConstants(
    FlextConstants,
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsExceptions,
    FlextCliConstantsFiles,
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
        FlextCliConstantsFiles,
        FlextCliConstantsOutput,
        FlextCliConstantsSettings,
    ):
        """CLI related constants."""


__all__: t.StrSequence = ("FlextCliConstants", "c")

c = FlextCliConstants
