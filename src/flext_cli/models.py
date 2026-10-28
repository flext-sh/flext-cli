# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m as flext_core_m

from flext_cli._models import (
    FlextCliConfigModels,
    FlextCliModelsAtomicPublication,
    FlextCliModelsAtomicState,
    FlextCliModelsAtomicSymlink,
    FlextCliModelsBase,
    FlextCliModelsColor,
    FlextCliModelsDocx,
    FlextCliModelsDocxDocument,
    FlextCliModelsDocxStyles,
    FlextCliModelsFileChange,
    FlextCliModelsFiles,
    FlextCliModelsMarkdown,
    FlextCliModelsPipeline,
    FlextCliModelsPptx,
    FlextCliModelsPptxPresentation,
    FlextCliModelsProcess,
    FlextCliModelsRules,
    FlextCliModelsTemplate,
    FlextCliModelsXlsx,
)


class FlextCliModels(flext_core_m):
    """FlextCli models extending FlextModels."""

    class Cli(
        FlextCliModelsAtomicState,
        FlextCliModelsBase,
        FlextCliModelsAtomicPublication,
        FlextCliModelsAtomicSymlink,
        FlextCliModelsColor,
        FlextCliConfigModels,
        FlextCliModelsDocx,
        FlextCliModelsDocxDocument,
        FlextCliModelsDocxStyles,
        FlextCliModelsFileChange,
        FlextCliModelsFiles,
        FlextCliModelsMarkdown,
        FlextCliModelsPipeline,
        FlextCliModelsPptx,
        FlextCliModelsPptxPresentation,
        FlextCliModelsProcess,
        FlextCliModelsRules,
        FlextCliModelsTemplate,
        FlextCliModelsXlsx,
    ):
        """CLI project namespace."""


m = FlextCliModels

__all__: list[str] = ["FlextCliModels", "m"]
