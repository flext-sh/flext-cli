# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. File Test Helper package.

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

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._file_test_helper.assertions import (
        FlextCliUtilitiesFileTestHelpersAssertions,
    )
    from flext_cli._utilities._file_test_helper.parsing import (
        FlextCliUtilitiesFileTestHelpersParsing,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesFileTestHelpersAssertions",
    "FlextCliUtilitiesFileTestHelpersParsing",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesFileTestHelpersAssertions": ".assertions",
        "FlextCliUtilitiesFileTestHelpersParsing": ".parsing",
    }),
    public_exports=__all__,
)
