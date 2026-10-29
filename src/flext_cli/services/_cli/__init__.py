# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services. Cli package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services._cli.flextcliservicecli_part_01 import FlextCliCliPart01
    from flext_cli.services._cli.flextcliservicecli_part_02 import FlextCliCliPart02
    from flext_cli.services._cli.flextcliservicecli_part_03 import FlextCliCliPart03
    from flext_cli.services._cli.flextcliservicecli_part_04 import FlextCliCliPart04
    from flext_cli.services._cli.flextcliservicecli_part_05 import FlextCliCliPart05
    from flext_cli.services._cli.flextcliservicecli_part_06 import FlextCliCliPart06


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
        "FlextCliCliPart01": ".flextcliservicecli_part_01",
        "FlextCliCliPart02": ".flextcliservicecli_part_02",
        "FlextCliCliPart03": ".flextcliservicecli_part_03",
        "FlextCliCliPart04": ".flextcliservicecli_part_04",
        "FlextCliCliPart05": ".flextcliservicecli_part_05",
        "FlextCliCliPart06": ".flextcliservicecli_part_06",
    }),
    public_exports=__all__,
)
