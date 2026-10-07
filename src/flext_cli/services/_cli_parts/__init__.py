# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services. Cli Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services._cli_parts.flextclicli_part_01 import FlextCliCliPart01
    from flext_cli.services._cli_parts.flextclicli_part_02 import FlextCliCliPart02
    from flext_cli.services._cli_parts.flextclicli_part_03 import FlextCliCliPart03
    from flext_cli.services._cli_parts.flextclicli_part_04 import FlextCliCliPart04
    from flext_cli.services._cli_parts.flextclicli_part_05 import FlextCliCliPart05
    from flext_cli.services._cli_parts.flextclicli_part_06 import FlextCliCliPart06


__all__: tuple[str, ...] = (
    "FlextCliCliPart01",
    "FlextCliCliPart02",
    "FlextCliCliPart03",
    "FlextCliCliPart04",
    "FlextCliCliPart05",
    "FlextCliCliPart06",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliCliPart01": ".flextclicli_part_01",
        "FlextCliCliPart02": ".flextclicli_part_02",
        "FlextCliCliPart03": ".flextclicli_part_03",
        "FlextCliCliPart04": ".flextclicli_part_04",
        "FlextCliCliPart05": ".flextclicli_part_05",
        "FlextCliCliPart06": ".flextclicli_part_06",
    }),
    public_exports=__all__,
)
