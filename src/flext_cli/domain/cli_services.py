"""CLI service container for dependency injection.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import ValidatedModel
from pydantic import Field


class CLIServiceContainer(ValidatedModel):
    """Service container for CLI dependency injection."""

    name: str = Field(..., description="Service container name")
    version: str = Field(..., description="Service container version")
