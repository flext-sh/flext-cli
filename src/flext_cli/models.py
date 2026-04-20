"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_core import m

from flext_cli import FlextCliModelsBase, FlextCliModelsPipeline


class FlextCliModels(m):
    """FlextCli models extending FlextModels."""

    class Cli(FlextCliModelsPipeline, FlextCliModelsBase):
        """CLI project namespace."""


m = FlextCliModels

__all__: list[str] = [
    "FlextCliModels",
    "m",
]
