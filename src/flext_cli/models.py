# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m as flext_core_m

from flext_cli._models import (
    FlextCliModelsAtomicQueries,
    FlextCliModelsAtomicState,
    FlextCliModelsBase,
    FlextCliModelsColor,
    FlextCliModelsConfig,
    FlextCliModelsDocx,
    FlextCliModelsFileChange,
    FlextCliModelsFiles,
    FlextCliModelsMarkdown,
    FlextCliModelsPipeline,
    FlextCliModelsPptx,
    FlextCliModelsProcess,
    FlextCliModelsProcessRuntime,
    FlextCliModelsRules,
    FlextCliModelsTemplate,
    FlextCliModelsXlsx,
)


class FlextCliModels(flext_core_m):
    """FlextCli models extending FlextModels."""

    class Cli(
        FlextCliModelsAtomicQueries,
        FlextCliModelsAtomicState,
        FlextCliModelsBase,
        FlextCliModelsColor,
        FlextCliModelsConfig,
        FlextCliModelsDocx,
        FlextCliModelsFileChange,
        FlextCliModelsFiles,
        FlextCliModelsMarkdown,
        FlextCliModelsPipeline,
        FlextCliModelsPptx,
        FlextCliModelsProcess,
        FlextCliModelsProcessRuntime,
        FlextCliModelsRules,
        FlextCliModelsTemplate,
        FlextCliModelsXlsx,
    ):
        """CLI project namespace."""


m = FlextCliModels

__all__: list[str] = ["FlextCliModels", "m"]
