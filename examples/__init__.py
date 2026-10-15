# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from examples.constants import ExamplesFlextCliConstants, c
    from examples.ex_01_getting_started import ExamplesFlextCliGettingStarted
    from examples.ex_05_authentication import ExamplesFlextCliAuthentication
    from examples.ex_06_settings import ExamplesFlextCliSettings
    from examples.ex_11_complete_integration import ExamplesFlextCliDataManager
    from examples.models import ExamplesFlextCliModels, m
    from examples.protocols import ExamplesFlextCliProtocols, p
    from examples.typings import ExamplesFlextCliTypes, t
    from examples.utilities import ExamplesFlextCliUtilities, u
    from flext_cli import s


__all__: tuple[str, ...] = (
    "ExamplesFlextCliAuthentication",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliDataManager",
    "ExamplesFlextCliGettingStarted",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliSettings",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ExamplesFlextCliAuthentication": ".ex_05_authentication",
        "ExamplesFlextCliConstants": ".constants",
        "ExamplesFlextCliDataManager": ".ex_11_complete_integration",
        "ExamplesFlextCliGettingStarted": ".ex_01_getting_started",
        "ExamplesFlextCliModels": ".models",
        "ExamplesFlextCliProtocols": ".protocols",
        "ExamplesFlextCliSettings": ".ex_06_settings",
        "ExamplesFlextCliTypes": ".typings",
        "ExamplesFlextCliUtilities": ".utilities",
        "c": ".constants",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "m": ".models",
        "p": ".protocols",
        "r": "flext_core",
        "s": "flext_cli",
        "t": ".typings",
        "u": ".utilities",
        "x": "flext_core",
    }),
    public_exports=__all__,
)
