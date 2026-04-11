"""FLEXT CLI constants."""

from __future__ import annotations

from flext_cli._constants.base import FlextCliConstantsBase
from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_cli._constants.errors import FlextCliConstantsErrors
from flext_cli._constants.output import FlextCliConstantsOutput
from flext_cli._constants.pipeline import FlextCliConstantsPipeline
from flext_cli._constants.settings import FlextCliConstantsSettings
from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
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

__all__ = ["FlextCliConstants", "c"]
