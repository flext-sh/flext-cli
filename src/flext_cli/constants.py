"""FLEXT CLI constants."""

from __future__ import annotations

from flext_cli import (
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsOutput,
    FlextCliConstantsPipeline,
    FlextCliConstantsSettings,
)
from flext_core import c


class FlextCliConstants(c):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsPipeline,
        FlextCliConstantsBase,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        FlextCliConstantsOutput,
        FlextCliConstantsSettings,
    ):
        """CLI related constants."""


c = FlextCliConstants

__all__: list[str] = ["FlextCliConstants", "c"]
