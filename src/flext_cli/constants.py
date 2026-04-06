"""FLEXT CLI constants."""

from __future__ import annotations

from flext_cli import (
    FlextCliConstantsBase,
    FlextCliConstantsConfig,
    FlextCliConstantsEnums,
)
from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsBase,
        FlextCliConstantsEnums,
        FlextCliConstantsConfig,
    ):
        """CLI related constants."""


c = FlextCliConstants

__all__ = ["FlextCliConstants", "c"]
