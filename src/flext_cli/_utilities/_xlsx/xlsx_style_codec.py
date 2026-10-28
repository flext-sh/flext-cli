"""Canonical MRO owner for typed XLSX visual-style translation.

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

from flext_cli._utilities import (
    FlextCliUtilitiesXlsxStyleBuilders,
    FlextCliUtilitiesXlsxStyleReaders,
)


class FlextCliUtilitiesXlsxStyleCodec(
    FlextCliUtilitiesXlsxStyleBuilders,
    FlextCliUtilitiesXlsxStyleReaders,
):
    """Compose vendor-to-model and model-to-vendor style translation once."""


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxStyleCodec",)
