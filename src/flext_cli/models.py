"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_cli import FlextCliModelsBase
from flext_core import FlextModels


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels."""

    class Cli(FlextCliModelsBase):
        """CLI project namespace."""


m = FlextCliModels

__all__ = [
    "FlextCliModels",
    "m",
]
