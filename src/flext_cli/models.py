"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._models.base import FlextCliModelsBase
from flext_cli._models.docx import FlextCliModelsDocx
from flext_cli._models.pipeline import FlextCliModelsPipeline
from flext_cli._models.pptx import FlextCliModelsPptx
from flext_cli._models.rules import FlextCliModelsRules
from flext_cli._models.template import FlextCliModelsTemplate
from flext_cli._models.xlsx import FlextCliModelsXlsx
from flext_core import FlextModels

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(
        FlextCliModelsPipeline,
        FlextCliModelsRules,
        FlextCliModelsBase,
        FlextCliModelsTemplate,
        FlextCliModelsXlsx,
        FlextCliModelsDocx,
        FlextCliModelsPptx,
    ):
        """CLI project namespace."""


# mro-j47u (codex): canonical facade rebinding is intentionally unannotated.
m = FlextCliModels

__all__: t.MutableSequenceOf[str] = ["FlextCliModels", "m"]
