"""Extracted facade class for json.

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

from flext_cli._utilities._json import FlextCliUtilitiesJsonNavigate


class FlextCliUtilitiesJson(
    FlextCliUtilitiesJsonNavigate,
):
    """Facade for json."""


__all__: list[str] = ["FlextCliUtilitiesJson"]
