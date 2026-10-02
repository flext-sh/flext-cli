"""Pydantic models for flext-cli examples only.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from examples._models_parts.examples_advanced import (
    ExamplesFlextCliModelsExamplesAdvanced,
)
from examples._models_parts.examples_common import ExamplesFlextCliModelsExamplesCommon
from examples._models_parts.examples_database import (
    ExamplesFlextCliModelsExamplesDatabase,
)


class ExamplesFlextCliModels:
    """Implementation part for ExamplesFlextCliModels."""

    class Examples(
        ExamplesFlextCliModelsExamplesCommon,
        ExamplesFlextCliModelsExamplesAdvanced,
        ExamplesFlextCliModelsExamplesDatabase,
    ):
        """Examples namespace for example-domain models."""


__all__: list[str] = ["ExamplesFlextCliModels"]
