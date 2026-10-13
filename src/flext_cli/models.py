"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._models.atomic_state import FlextCliModelsAtomicState
from flext_cli._models.atomic_symlink import FlextCliModelsAtomicSymlink
from flext_cli._models.base import FlextCliModelsBase
from flext_cli._models.config import FlextCliConfigModels
from flext_cli._models.docx import FlextCliModelsDocx
from flext_cli._models.docx_document import FlextCliModelsDocxDocument
from flext_cli._models.docx_styles import FlextCliModelsDocxStyles
from flext_cli._models.pipeline import FlextCliModelsPipeline
from flext_cli._models.pptx import FlextCliModelsPptx
from flext_cli._models.pptx_presentation import FlextCliModelsPptxPresentation
from flext_cli._models.process import FlextCliModelsProcess
from flext_cli._models.rules import FlextCliModelsRules
from flext_cli._models.template import FlextCliModelsTemplate
from flext_cli._models.xlsx import FlextCliModelsXlsx
from flext_core import FlextModels

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(
        FlextCliModelsAtomicState,
        FlextCliModelsBase,
        FlextCliModelsAtomicSymlink,
        FlextCliConfigModels,
        FlextCliModelsDocx,
        FlextCliModelsDocxDocument,
        FlextCliModelsDocxStyles,
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
