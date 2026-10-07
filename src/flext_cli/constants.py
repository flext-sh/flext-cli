"""Flext CLI constants — flat MRO facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._constants import (
    FlextCliConstantsBase,
    FlextCliConstantsConfig,
    FlextCliConstantsDefaults,
    FlextCliConstantsDocx,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsFiles,
    FlextCliConstantsOutput,
    FlextCliConstantsPptx,
    FlextCliConstantsSettings,
    FlextCliConstantsXlsx,
    FlextCliConstantsXlsxFutureFunctions,
)
from flext_core import FlextConstants, t


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
