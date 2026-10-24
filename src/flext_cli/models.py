# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextModels

from flext_cli._models import (
    FlextCliConfigModels,
    FlextCliModelsAtomicPublication,
    FlextCliModelsAtomicState,
    FlextCliModelsAtomicSymlink,
    FlextCliModelsBase,
    FlextCliModelsDocx,
    FlextCliModelsDocxDocument,
    FlextCliModelsDocxStyles,
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

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(
        FlextCliModelsAtomicState,
        FlextCliModelsBase,
        FlextCliModelsAtomicPublication,
        FlextCliModelsAtomicSymlink,
        FlextCliConfigModels,
        FlextCliModelsDocx,
        FlextCliModelsDocxDocument,
        FlextCliModelsDocxStyles,
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


# mro-j47u (codex): canonical facade rebinding is intentionally unannotated.
m = FlextCliModels

__all__: t.MutableSequenceOf[str] = ["FlextCliModels", "m"]
