# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from examples.constants import ExamplesFlextCliConstants, c
    from examples.ex_01_getting_started import ExamplesFlextCliGettingStarted
    from examples.ex_05_authentication import Ex05Authentication
    from examples.ex_06_settings import Ex06Settings
    from examples.ex_11_complete_integration import DataManagerCLI
    from examples.models import ExamplesFlextCliModels, m
    from examples.protocols import ExamplesFlextCliProtocols, p
    from examples.typings import ExamplesFlextCliTypes, t
    from examples.utilities import ExamplesFlextCliUtilities, u
    from flext_cli import d, e, h, r, s, x
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": (
            "ExamplesFlextCliConstants",
            "c",
        ),
        ".ex_01_getting_started": ("ExamplesFlextCliGettingStarted",),
        ".ex_05_authentication": ("Ex05Authentication",),
        ".ex_06_settings": ("Ex06Settings",),
        ".ex_11_complete_integration": ("DataManagerCLI",),
        ".models": (
            "ExamplesFlextCliModels",
            "m",
        ),
        ".protocols": (
            "ExamplesFlextCliProtocols",
            "p",
        ),
        ".typings": (
            "ExamplesFlextCliTypes",
            "t",
        ),
        ".utilities": (
            "ExamplesFlextCliUtilities",
            "u",
        ),
        "flext_cli": (
            "d",
            "e",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "DataManagerCLI",
    "Ex05Authentication",
    "Ex06Settings",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliGettingStarted",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliProtocols",
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
]
