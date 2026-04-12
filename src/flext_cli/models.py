"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_cli import FlextCliModelsBase, FlextCliModelsPipeline
from flext_core import FlextModels


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(FlextCliModelsPipeline, FlextCliModelsBase):
        """CLI project namespace."""


m = FlextCliModels

__all__: list[str] = [
    "FlextCliModels",
    "m",
]
