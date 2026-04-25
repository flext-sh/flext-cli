"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

from flext_core import FlextConstants

from flext_cli import (
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsOutput,
    FlextCliConstantsPipeline,
    FlextCliConstantsSettings,
)


class FlextCliConstants(
    FlextConstants,
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
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
        FlextCliConstantsOutput,
        FlextCliConstantsSettings,
    ):
        """CLI related constants."""


__all__: list[str] = ["FlextCliConstants", "c"]

c = FlextCliConstants
