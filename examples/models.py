"""Pydantic models for flext-cli examples only.

All example-domain models live here; examples MUST NOT define models inline.
Import: from models import ... (when run from examples/ dir).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliModels

from ._models_parts.examplesflextclimodels_part_01 import (
    ExamplesFlextCliModels as ExamplesFlextCliModelsPart01,
)


class ExamplesFlextCliModels(ExamplesFlextCliModelsPart01, FlextCliModels):
    """Public facade for ExamplesFlextCliModels."""


m = ExamplesFlextCliModels

__all__: list[str] = ["ExamplesFlextCliModels", "m"]
