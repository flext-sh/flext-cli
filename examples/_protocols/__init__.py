# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples._protocols.examples_advanced import (
        ExamplesFlextCliProtocolsExamplesAdvanced,
    )
    from examples._protocols.examples_common import (
        ExamplesFlextCliProtocolsExamplesCommon,
    )
    from examples._protocols.examples_database import (
        ExamplesFlextCliProtocolsExamplesDatabase,
    )


__all__: tuple[str, ...] = (
    "ExamplesFlextCliProtocolsExamplesAdvanced",
    "ExamplesFlextCliProtocolsExamplesCommon",
    "ExamplesFlextCliProtocolsExamplesDatabase",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "ExamplesFlextCliProtocolsExamplesAdvanced": ".examples_advanced",
        "ExamplesFlextCliProtocolsExamplesCommon": ".examples_common",
        "ExamplesFlextCliProtocolsExamplesDatabase": ".examples_database",
    },
    public_exports=__all__,
    deferred_members={
        "ExamplesFlextCliProtocolsExamplesAdvanced": ("AppSettingsAdvanced",),
        "ExamplesFlextCliProtocolsExamplesCommon": (
            "GreetingRequest",
            "MyAppSettings",
        ),
        "ExamplesFlextCliProtocolsExamplesDatabase": ("AdvancedDatabaseConfig",),
    },
)
