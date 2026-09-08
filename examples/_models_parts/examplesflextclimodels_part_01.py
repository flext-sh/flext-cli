"""Pydantic models for flext-cli examples only."""

from __future__ import annotations

from .examples_advanced import ExamplesFlextCliModelsExamplesAdvanced
from .examples_common import ExamplesFlextCliModelsExamplesCommon
from .examples_database import ExamplesFlextCliModelsExamplesDatabase


class ExamplesFlextCliModels:
    """Implementation part for ExamplesFlextCliModels."""

    class Examples(
        ExamplesFlextCliModelsExamplesCommon,
        ExamplesFlextCliModelsExamplesAdvanced,
        ExamplesFlextCliModelsExamplesDatabase,
    ):
        """Examples namespace for example-domain models."""


__all__: list[str] = ["ExamplesFlextCliModels"]
