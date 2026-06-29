"""Pydantic models for flext-cli examples only.

All example-domain models live here; examples MUST NOT define models inline.
Import: from models import ... (when run from examples/ dir).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib as _importlib

from examples._models_parts.examplesflextclimodels_part_01 import (
    ExamplesFlextCliModels as ExamplesFlextCliModelsPart01,
)
from flext_cli import m as flext_cli_m


class ExamplesFlextCliModels(
    ExamplesFlextCliModelsPart01,
    flext_cli_m,
):
    """Public facade for ExamplesFlextCliModels."""


m: type[ExamplesFlextCliModels] = ExamplesFlextCliModels

__all__: list[str] = ["ExamplesFlextCliModels", "m"]


# Bind part-module facade names for runtime class-level lookups.
setattr(
    _importlib.import_module("examples._models_parts.examplesflextclimodels_part_01"),
    "ExamplesFlextCliModels",
    ExamplesFlextCliModels,
)
