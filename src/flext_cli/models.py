"""FlextCli models module - Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._models import (
    FlextCliModelsBase,
    FlextCliModelsDocx,
    FlextCliModelsPipeline,
    FlextCliModelsPptx,
    FlextCliModelsRules,
    FlextCliModelsTemplate,
    FlextCliModelsXlsx,
)
from flext_core import FlextModels

if TYPE_CHECKING:
    from flext_cli import t


from flext_cli._models.process import FlextCliModelsProcess


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
        FlextCliModelsProcess,
    ):
        """CLI project namespace."""


# mro-j47u (codex): canonical facade rebinding is intentionally unannotated.
m = FlextCliModels

__all__: t.MutableSequenceOf[str] = ["FlextCliModels", "m"]
