"""Generic TOML helpers shared through ``u.Cli.toml_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities import (
    FlextCliUtilitiesTomlPart01,
    FlextCliUtilitiesTomlPart02,
    FlextCliUtilitiesTomlPart03,
    FlextCliUtilitiesTomlPart04,
    FlextCliUtilitiesTomlPart05,
    FlextCliUtilitiesTomlPart06,
    FlextCliUtilitiesTomlPart07,
)


class FlextCliUtilitiesToml(
    FlextCliUtilitiesTomlPart01,
    FlextCliUtilitiesTomlPart02,
    FlextCliUtilitiesTomlPart03,
    FlextCliUtilitiesTomlPart04,
    FlextCliUtilitiesTomlPart05,
    FlextCliUtilitiesTomlPart06,
    FlextCliUtilitiesTomlPart07,
):
    """Public facade for FlextCliUtilitiesToml."""


__all__: list[str] = ["FlextCliUtilitiesToml"]
