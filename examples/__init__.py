# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._models_parts": ("_models_parts",),
            ".constants": ("ExamplesFlextCliConstants", "c"),
            ".ex_01_getting_started": ("ExamplesFlextCliGettingStarted",),
            ".ex_05_authentication": ("Ex05Authentication",),
            ".ex_06_settings": ("Ex06Settings",),
            ".ex_11_complete_integration": ("DataManagerCLI",),
            ".models": ("ExamplesFlextCliModels", "m"),
            ".protocols": ("ExamplesFlextCliProtocols", "p"),
            ".typings": ("ExamplesFlextCliTypes", "t"),
            ".utilities": ("ExamplesFlextCliUtilities", "u"),
            "flext_cli": ("s",),
            "flext_core": ("d", "e", "h", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
