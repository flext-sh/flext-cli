# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from examples import _models_parts
    from examples.constants import ExamplesFlextCliConstants, c
    from examples.ex_01_getting_started import ExamplesFlextCliGettingStarted
    from examples.ex_05_authentication import Ex05Authentication
    from examples.ex_06_settings import Ex06Settings
    from examples.ex_11_complete_integration import DataManagerCLI
    from examples.models import ExamplesFlextCliModels, m
    from examples.protocols import ExamplesFlextCliProtocols, p
    from examples.typings import ExamplesFlextCliTypes, t
    from examples.utilities import ExamplesFlextCliUtilities, u
    from flext_cli import s
    from flext_core import d, e, h, r, x


__all__: tuple[str, ...] = (
    "DataManagerCLI",
    "Ex05Authentication",
    "Ex06Settings",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliGettingStarted",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "_models_parts",
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
        "DataManagerCLI": ".ex_11_complete_integration",
        "Ex05Authentication": ".ex_05_authentication",
        "Ex06Settings": ".ex_06_settings",
        "ExamplesFlextCliConstants": ".constants",
        "ExamplesFlextCliGettingStarted": ".ex_01_getting_started",
        "ExamplesFlextCliModels": ".models",
        "ExamplesFlextCliProtocols": ".protocols",
        "ExamplesFlextCliTypes": ".typings",
        "ExamplesFlextCliUtilities": ".utilities",
        "_models_parts": "._models_parts",
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
