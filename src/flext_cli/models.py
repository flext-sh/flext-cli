"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from flext_cli._models.base import FlextCliModelsBase
from flext_cli._models.pipeline import FlextCliModelsPipeline
from flext_cli._models.rules import FlextCliModelsRules
from flext_cli._models.template import FlextCliModelsTemplate
from flext_core import FlextModels

if TYPE_CHECKING:
    from flext_cli.typings import t


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    ConfigDict: TypeAlias = FlextModels.ConfigDict
    SettingsConfigDict: TypeAlias = FlextModels.SettingsConfigDict

    class Cli(
        FlextCliModelsPipeline,
        FlextCliModelsRules,
        FlextCliModelsBase,
        FlextCliModelsTemplate,
    ):
        """CLI project namespace."""


m: type[FlextCliModels] = FlextCliModels

__all__: t.MutableSequenceOf[str] = [
    "FlextCliModels",
    "m",
]
