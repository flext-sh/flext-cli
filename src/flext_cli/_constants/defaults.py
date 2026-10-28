"""Flext Cli immutable declaration-default constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliConstantsDefaults:
    """Immutable default values shared by CLI declaration models."""

    EMPTY_JSON_MAPPING: ClassVar[t.JsonMapping] = MappingProxyType({})

    EMPTY_STR_MAPPING: ClassVar[Mapping[str, str]] = MappingProxyType({})


__all__: list[str] = ["FlextCliConstantsDefaults"]
