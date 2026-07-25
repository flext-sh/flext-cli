"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

from flext_cli._constants.base import FlextCliConstantsBase
from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_cli._constants.errors import FlextCliConstantsErrors
from flext_cli._constants.exceptions import FlextCliConstantsExceptions
from flext_cli._constants.files import FlextCliConstantsFiles
from flext_cli._constants.output import FlextCliConstantsOutput
from flext_cli._constants.pipeline import FlextCliConstantsPipeline
from flext_cli._constants.settings import FlextCliConstantsSettings
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
