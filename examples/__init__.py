# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from examples.constants import ExamplesFlextCliConstants, c
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
    "ExamplesFlextCliConstants",
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
