"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_core import FlextModels

from flext_cli import FlextCliModelsBase, FlextCliModelsPipeline


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(FlextCliModelsPipeline, FlextCliModelsBase):
        """CLI project namespace."""


m: type[FlextCliModels] = FlextCliModels

__all__: list[str] = [
    "FlextCliModels",
    "m",
]
