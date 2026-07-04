"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_cli._models.base import FlextCliModelsBase
from flext_cli._models.pipeline import FlextCliModelsPipeline
from flext_cli._models.rules import FlextCliModelsRules
from flext_cli.typings import t
from flext_core import FlextModels


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    ConfigDict = FlextModels.ConfigDict
    SettingsConfigDict = FlextModels.SettingsConfigDict

    class Cli(FlextCliModelsPipeline, FlextCliModelsRules, FlextCliModelsBase):
        """CLI project namespace."""


m: type[FlextCliModels] = FlextCliModels

__all__: t.MutableSequenceOf[str] = [
    "FlextCliModels",
    "m",
]
