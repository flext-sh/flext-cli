"""Flext CLI constants — flat MRO facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import t
from flext_cli._constants import FlextCliConstantsBase
from flext_cli._constants import FlextCliConstantsConfig
from flext_cli._constants import FlextCliConstantsDefaults
from flext_cli._constants import FlextCliConstantsDocx
from flext_cli._constants import FlextCliConstantsEnums
from flext_cli._constants import FlextCliConstantsErrors
from flext_cli._constants import FlextCliConstantsFiles
from flext_cli._constants import FlextCliConstantsOutput
from flext_cli._constants import FlextCliConstantsPptx
from flext_cli._constants import FlextCliConstantsSettings
from flext_cli._constants import FlextCliConstantsXlsx
from flext_cli._constants import FlextCliConstantsXlsxFutureFunctions
from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsBase,
        FlextCliConstantsConfig,
        FlextCliConstantsDefaults,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        FlextCliConstantsDocx,
        FlextCliConstantsPptx,
        FlextCliConstantsFiles,
        FlextCliConstantsOutput,
        FlextCliConstantsSettings,
        FlextCliConstantsXlsx,
        FlextCliConstantsXlsxFutureFunctions,
    ):
        """CLI related constants."""


c = FlextCliConstants

__all__: t.StrSequence = ("FlextCliConstants", "c")
