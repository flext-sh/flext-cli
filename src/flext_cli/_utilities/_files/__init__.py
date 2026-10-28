# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Files package.

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
    from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
    from flext_cli._utilities._files.flextcliutilitiesfiles_part_05 import (
        FlextCliUtilitiesFilesPart05,
    )
    from flext_cli._utilities._files.flextcliutilitiesfiles_part_06 import (
        FlextCliUtilitiesFilesPart06,
    )
    from flext_cli._utilities._files.formats import FlextCliUtilitiesFilesPart04
    from flext_cli._utilities._files.text_formats import FlextCliUtilitiesFilesPart01
    from flext_cli._utilities._files.writes import FlextCliUtilitiesFilesPart02


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesFilesPart01",
    "FlextCliUtilitiesFilesPart02",
    "FlextCliUtilitiesFilesPart03",
    "FlextCliUtilitiesFilesPart04",
    "FlextCliUtilitiesFilesPart05",
    "FlextCliUtilitiesFilesPart06",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesFilesPart01": ".text_formats",
        "FlextCliUtilitiesFilesPart02": ".writes",
        "FlextCliUtilitiesFilesPart03": ".binary_reads",
        "FlextCliUtilitiesFilesPart04": ".formats",
        "FlextCliUtilitiesFilesPart05": ".flextcliutilitiesfiles_part_05",
        "FlextCliUtilitiesFilesPart06": ".flextcliutilitiesfiles_part_06",
    }),
    public_exports=__all__,
)
