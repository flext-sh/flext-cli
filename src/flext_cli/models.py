# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from flext_core import FlextModels

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
    FlextCliModelsTableRender,
    FlextCliModelsTemplate,
    FlextCliModelsXlsx,
)


class FlextCliModels(FlextModels):
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
        FlextCliModelsTableRender,
        FlextCliModelsTemplate,
        FlextCliModelsXlsx,
    ):
        """CLI project namespace."""

        if TYPE_CHECKING:
            ProcessNativeQualificationReceipt: TypeAlias = (
                FlextCliModelsProcess.ProcessNativeQualificationReceipt
            )
            ProcessNativeQualificationReport: TypeAlias = (
                FlextCliModelsProcess.ProcessNativeQualificationReport
            )
            LocalDefinitionsOptions: TypeAlias = (
                FlextCliModelsRules.LocalDefinitionsOptions
            )


m = FlextCliModels

__all__: list[str] = ["FlextCliModels", "m"]
