"""FLEXT CLI constants."""

from __future__ import annotations

from flext_cli._constants.base import FlextCliConstantsBase
from flext_cli._constants.config import FlextCliConstantsConfig
from flext_cli._constants.enums import FlextCliConstantsEnums
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
