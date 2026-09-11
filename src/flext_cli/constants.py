"""Flext CLI constants — flat MRO facade."""

from __future__ import annotations

from flext_core import c, t

from ._constants.base import FlextCliConstantsBase
from ._constants.config import FlextCliConstantsConfig
from ._constants.docx import FlextCliConstantsDocx
from ._constants.enums import FlextCliConstantsEnums
from ._constants.errors import FlextCliConstantsErrors
from ._constants.exceptions import FlextCliConstantsExceptions
from ._constants.files import FlextCliConstantsFiles
from ._constants.output import FlextCliConstantsOutput
from ._constants.pptx import FlextCliConstantsPptx
from ._constants.settings import FlextCliConstantsSettings
from ._constants.xlsx import FlextCliConstantsXlsx
from ._constants.xlsx_future_functions import FlextCliConstantsXlsxFutureFunctions


class FlextCliConstants(c):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsBase,
        FlextCliConstantsConfig,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        FlextCliConstantsDocx,
        FlextCliConstantsPptx,
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
