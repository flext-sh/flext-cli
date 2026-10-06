"""Test-oriented file helpers generalized for reuse through ``u.Cli``.

These operations are generic enough to be used by tests, examples, and
maintenance scripts, but were originally duplicated in ``flext-tests``.
They live here so ``flext-tests`` can delegate to ``u.Cli`` instead of
reimplementing them.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_01 import (
    FlextCliUtilitiesFileTestHelpersMixinPart01,
)
from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_02 import (
    FlextCliUtilitiesFileTestHelpersMixinPart02,
)
from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_03 import (
    FlextCliUtilitiesFileTestHelpersMixinPart03,
)
from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04 import (
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
