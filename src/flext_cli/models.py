"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_cli import FlextCliModelsBase, FlextCliModelsPipeline, FlextCliModelsRules, t
from flext_core import FlextModels


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(FlextCliModelsPipeline, FlextCliModelsRules, FlextCliModelsBase):
        """CLI project namespace."""


m: type[FlextCliModels] = FlextCliModels

__all__: t.MutableSequenceOf[str] = [
    "FlextCliModels",
    "m",
]

m = FlextCliModels
