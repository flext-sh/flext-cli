"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_core import FlextModels

from flext_cli._models.base import FlextCliModelsBase
from flext_cli._models.pipeline import FlextCliModelsPipeline


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(FlextCliModelsPipeline, FlextCliModelsBase):
        """CLI project namespace."""


m: type[FlextCliModels] = FlextCliModels

__all__: list[str] = [
    "FlextCliModels",
    "m",
]
