"""Canonical MRO owner for typed XLSX visual-style translation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._utilities import FlextCliUtilitiesXlsxStyleBuilders
from flext_cli._utilities import FlextCliUtilitiesXlsxStyleReaders

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesXlsxStyleCodec(
    FlextCliUtilitiesXlsxStyleBuilders,
    FlextCliUtilitiesXlsxStyleReaders,
):
    """Compose vendor-to-model and model-to-vendor style translation once."""


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesXlsxStyleCodec",)
