"""Test-oriented file helpers generalized for reuse through ``u.Cli``.

These operations are generic enough to be used by tests, examples, and
maintenance scripts, but were originally duplicated in ``flext-tests``.
They live here so ``flext-tests`` can delegate to ``u.Cli`` instead of
reimplementing them.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities import (
    FlextCliUtilitiesFileTestHelpersMixinPart01,
    FlextCliUtilitiesFileTestHelpersMixinPart02,
    FlextCliUtilitiesFileTestHelpersMixinPart03,
    FlextCliUtilitiesFileTestHelpersMixinPart04,
)


class FlextCliUtilitiesFileTestHelpersMixin(
    FlextCliUtilitiesFileTestHelpersMixinPart01,
    FlextCliUtilitiesFileTestHelpersMixinPart02,
    FlextCliUtilitiesFileTestHelpersMixinPart03,
    FlextCliUtilitiesFileTestHelpersMixinPart04,
):
    """Public facade for FlextCliUtilitiesFileTestHelpersMixin."""


__all__: list[str] = ["FlextCliUtilitiesFileTestHelpersMixin"]
