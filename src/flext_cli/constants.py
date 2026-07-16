"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

from ._constants import (
    FlextCliConstantsBase,
    FlextCliConstantsConfig,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsExceptions,
    FlextCliConstantsFiles,
    FlextCliConstantsOutput,
    FlextCliConstantsPipeline,
    FlextCliConstantsSettings,
    FlextCliConstantsXlsx,
    FlextCliConstantsXlsxFutureFunctions,
)
from flext_core import c, t


class FlextCliConstants(c):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsPipeline,
        FlextCliConstantsBase,
        FlextCliConstantsConfig,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        FlextCliConstantsExceptions,
        FlextCliConstantsFiles,
        FlextCliConstantsOutput,
        FlextCliConstantsSettings,
        FlextCliConstantsXlsx,
        FlextCliConstantsXlsxFutureFunctions,
    ):
        """CLI related constants."""


c = FlextCliConstants

__all__: t.StrSequence = ("FlextCliConstants", "c")
