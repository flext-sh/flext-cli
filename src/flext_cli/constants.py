# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext CLI constants — flat MRO facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextConstants

from flext_cli._constants import (
    FlextCliConstantsBase,
    FlextCliConstantsConfig,
    FlextCliConstantsDefaults,
    FlextCliConstantsDocx,
    FlextCliConstantsEnums,
    FlextCliConstantsErrors,
    FlextCliConstantsFiles,
    FlextCliConstantsMarkdown,
    FlextCliConstantsOutput,
    FlextCliConstantsPptx,
    FlextCliConstantsSettings,
    FlextCliConstantsXlsx,
    FlextCliConstantsXlsxFutureFunctions,
)


class FlextCliConstants(FlextConstants):
    """Constants for Flext CLI."""

    class Cli(
        FlextCliConstantsBase,
        FlextCliConstantsConfig,
        FlextCliConstantsDefaults,
        FlextCliConstantsDocx,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        FlextCliConstantsFiles,
        FlextCliConstantsMarkdown,
        FlextCliConstantsOutput,
        FlextCliConstantsPptx,
        FlextCliConstantsSettings,
        FlextCliConstantsXlsx,
        FlextCliConstantsXlsxFutureFunctions,
    ):
        """CLI related constants."""


c = FlextCliConstants
__all__: list[str] = ["FlextCliConstants", "c"]
