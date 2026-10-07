"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._models import FlextCliModelsBase
from flext_cli._models import FlextCliModelsDocx
from flext_cli._models import FlextCliModelsPipeline
from flext_cli._models import FlextCliModelsPptx
from flext_cli._models import FlextCliModelsRules
from flext_cli._models import FlextCliModelsTemplate
from flext_cli._models import FlextCliModelsXlsx
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
