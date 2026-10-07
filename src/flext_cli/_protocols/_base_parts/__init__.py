# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols. Base Parts package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_01 import (
        FlextCliProtocolsBasePart01,
    )
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_02 import (
        FlextCliProtocolsBasePart02,
    )
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_03 import (
        FlextCliProtocolsBasePart03,
    )
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_04 import (
        FlextCliProtocolsBasePart04,
    )
    from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_05 import (
        FlextCliProtocolsBasePart05,
    )


__all__: tuple[str, ...] = (
    "FlextCliProtocolsBasePart01",
    "FlextCliProtocolsBasePart02",
    "FlextCliProtocolsBasePart03",
    "FlextCliProtocolsBasePart04",
    "FlextCliProtocolsBasePart05",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliProtocolsBasePart01": ".flextcliprotocolsbase_part_01",
        "FlextCliProtocolsBasePart02": ".flextcliprotocolsbase_part_02",
        "FlextCliProtocolsBasePart03": ".flextcliprotocolsbase_part_03",
        "FlextCliProtocolsBasePart04": ".flextcliprotocolsbase_part_04",
        "FlextCliProtocolsBasePart05": ".flextcliprotocolsbase_part_05",
    }),
    public_exports=__all__,
)
