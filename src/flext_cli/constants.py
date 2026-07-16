"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

# NOTE (mro-0ftd.3.7.2, operator-authorized cross-lane fix): import direct from
# submodules (mirrors models.py) because the generated ._constants barrel is empty
# (__all__ = ()); the codegen that would repopulate it is itself blocked by this break.
from ._constants.base import FlextCliConstantsBase
from ._constants.config import FlextCliConstantsConfig
from ._constants.enums import FlextCliConstantsEnums
from ._constants.errors import FlextCliConstantsErrors
from ._constants.exceptions import FlextCliConstantsExceptions
from ._constants.files import FlextCliConstantsFiles
from ._constants.output import FlextCliConstantsOutput
from ._constants.pipeline import FlextCliConstantsPipeline
from ._constants.settings import FlextCliConstantsSettings
from ._constants.xlsx import FlextCliConstantsXlsx
from ._constants.xlsx_future_functions import FlextCliConstantsXlsxFutureFunctions
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
