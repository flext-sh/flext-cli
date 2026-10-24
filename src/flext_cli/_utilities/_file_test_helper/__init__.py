# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. File Test Helper package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._file_test_helper.flextcliutilitiesfiletesthelpersmixin_part_02 import (
        FlextCliUtilitiesFileTestHelpersMixinPart02,
    )
    from flext_cli._utilities._file_test_helper.flextcliutilitiesfiletesthelpersmixin_part_04 import (
        FlextCliUtilitiesFileTestHelpersMixinPart04,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesFileTestHelpersMixinPart02",
    "FlextCliUtilitiesFileTestHelpersMixinPart04",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesFileTestHelpersMixinPart02": (
            ".flextcliutilitiesfiletesthelpersmixin_part_02"
        ),
        "FlextCliUtilitiesFileTestHelpersMixinPart04": (
            ".flextcliutilitiesfiletesthelpersmixin_part_04"
        ),
    }),
    public_exports=__all__,
)
