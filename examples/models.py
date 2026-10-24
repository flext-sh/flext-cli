# AUTO-GENERATED FILE — Regenerate with: make gen
"""Pydantic models for flext-cli examples only.

All example-domain models live here; examples MUST NOT define models inline.
Import: from models import ... (when run from examples/ dir).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from examples._models import (
    ExamplesFlextCliModelsExamplesAdvanced,
    ExamplesFlextCliModelsExamplesCommon,
    ExamplesFlextCliModelsExamplesDatabase,
    ExamplesFlextCliModelsPart01,
)
from flext_cli import FlextCliModels


class ExamplesFlextCliModels(
    ExamplesFlextCliModelsExamplesAdvanced,
    ExamplesFlextCliModelsExamplesCommon,
    ExamplesFlextCliModelsExamplesDatabase,
    ExamplesFlextCliModelsPart01,
    FlextCliModels,
):
    """Public facade for ExamplesFlextCliModels."""


m = ExamplesFlextCliModels

__all__: list[str] = ["ExamplesFlextCliModels", "m"]
