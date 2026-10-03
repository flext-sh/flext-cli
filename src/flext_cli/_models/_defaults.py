"""Immutable default values shared by CLI declaration models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType

from flext_cli import t

EMPTY_JSON_MAPPING: t.JsonMapping = MappingProxyType({})

EMPTY_STR_MAPPING: t.StrMapping = MappingProxyType({})


__all__: t.VariadicTuple[str] = ("EMPTY_JSON_MAPPING", "EMPTY_STR_MAPPING")
