"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from flext_cli import t
from flext_core import m

from ._models.base import FlextCliModelsBase
from ._models.docx import FlextCliModelsDocx
from ._models.pipeline import FlextCliModelsPipeline
from ._models.pptx import FlextCliModelsPptx
from ._models.rules import FlextCliModelsRules
from ._models.template import FlextCliModelsTemplate
from ._models.xlsx import FlextCliModelsXlsx


class FlextCliModels(m):
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
