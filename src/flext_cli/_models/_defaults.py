"""Immutable default values shared by CLI declaration models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import ClassVar

from flext_cli import t


class FlextCliModelsDefaults:
    """Canonical namespace owner."""

    EMPTY_JSON_MAPPING: ClassVar[t.JsonMapping] = MappingProxyType({})

    EMPTY_STR_MAPPING: ClassVar[t.StrMapping] = MappingProxyType({})


__all__: t.VariadicTuple[str] = ("FlextCliModelsDefaults",)
