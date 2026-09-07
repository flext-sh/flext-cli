# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from enum import StrEnum, unique
    from typing import TYPE_CHECKING, Final

    from flext_cli import d, e, h, r, s, x

    from . import _models_parts as _models_parts
    from .constants import ExamplesFlextCliConstants, ExamplesFlextCliConstants as c
    from .ex_01_getting_started import ExamplesFlextCliGettingStarted
    from .ex_05_authentication import Ex05Authentication
    from .ex_06_settings import Ex06Settings
    from .ex_11_complete_integration import DataManagerCLI
    from .models import ExamplesFlextCliModels, ExamplesFlextCliModels as m
    from .protocols import ExamplesFlextCliProtocols, ExamplesFlextCliProtocols as p
    from .typings import ExamplesFlextCliTypes, ExamplesFlextCliTypes as t
    from .utilities import ExamplesFlextCliUtilities, ExamplesFlextCliUtilities as u
__all__: tuple[str, ...] = (
    "TYPE_CHECKING",
    "DataManagerCLI",
    "Ex05Authentication",
    "Ex06Settings",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliGettingStarted",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "Final",
    "MappingProxyType",
    "StrEnum",
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
    "unique",
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
            "enum": ("StrEnum", "unique"),
            "flext_cli": ("d", "e", "h", "r", "s", "x"),
            "types": ("MappingProxyType",),
            "typing": ("Final", "TYPE_CHECKING"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
