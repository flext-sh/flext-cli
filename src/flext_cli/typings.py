"""CLI type facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeVar

from flext_cli._typings.base import FlextCliTypesBase
from flext_cli._typings.domain import FlextCliTypesDomain
from flext_cli._typings.pipeline import FlextCliTypesPipeline
from flext_cli._typings.xlsx import FlextCliTypesXlsx
from flext_core import FlextTypes


class FlextCliTypes(FlextTypes):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(
        FlextCliTypesPipeline,
        FlextCliTypesDomain,
        FlextCliTypesBase,
        FlextCliTypesXlsx,
    ):
        """CLI types namespace for cross-project access."""


t = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]

type PhysicalState = tuple[int, int, int, int | None, int | None]

type DirectoryPhysicalState = tuple[int, int, int, int, int | None, int | None]

T = TypeVar("T")
