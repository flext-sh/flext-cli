"""Pydantic model configuration owner for the CLI utilities facade.

The facade binds this ``model_config`` through an identity alias so the
class-typed ``Cli`` namespace attribute survives pydantic model construction
through ``ignored_types`` while the authored ConfigDict statement stays out of
the generated facade body.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m


class FlextCliUtilitiesModelConfig:
    """Pydantic model configuration owner for the CLI utilities facade."""

    model_config = m.ConfigDict(ignored_types=(type,))


__all__: list[str] = ["FlextCliUtilitiesModelConfig"]
