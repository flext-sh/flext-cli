# AUTO-GENERATED FILE — Regenerate with: make gen
"""CLI type facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from flext_core import t as flext_core_t

from flext_cli._typings import (
    FlextCliTypesBase,
    FlextCliTypesDomain,
    FlextCliTypesPipeline,
    FlextCliTypesXlsx,
)


class FlextCliTypes(flext_core_t):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(
        FlextCliTypesBase,
        FlextCliTypesDomain,
        FlextCliTypesPipeline,
        FlextCliTypesXlsx,
    ):
        """CLI types namespace for cross-project access."""


t = FlextCliTypes


type PhysicalState = tuple[int, int, int, int | None, int | None]

type DirectoryPhysicalState = tuple[int, int, int, int, int | None, int | None]

T = TypeVar("T")


type RenameAt2 = Callable[[int, bytes, int, bytes, int], int]


type DirectoryChainInspection = tuple[
    Path,
    os.stat_result,
    tuple[tuple[int, int], ...],
    flext_core_tuple[Path, ...],
]
__all__: list[str] = ["FlextCliTypes", "t"]
