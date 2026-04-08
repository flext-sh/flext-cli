# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from examples.constants import (
        ExamplesFlextCliConstants,
        ExamplesFlextCliConstants as c,
    )
    from examples.models import ExamplesFlextCliModels, ExamplesFlextCliModels as m
    from examples.protocols import (
        ExamplesFlextCliProtocols,
        ExamplesFlextCliProtocols as p,
    )
    from examples.typings import ExamplesFlextCliTypes, ExamplesFlextCliTypes as t
    from examples.utilities import (
        ExamplesFlextCliUtilities,
        ExamplesFlextCliUtilities as u,
    )
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_core.service import s
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("ExamplesFlextCliConstants",),
        ".models": ("ExamplesFlextCliModels",),
        ".protocols": ("ExamplesFlextCliProtocols",),
        ".typings": ("ExamplesFlextCliTypes",),
        ".utilities": ("ExamplesFlextCliUtilities",),
        "flext_core.decorators": ("d",),
        "flext_core.exceptions": ("e",),
        "flext_core.handlers": ("h",),
        "flext_core.mixins": ("x",),
        "flext_core.result": ("r",),
        "flext_core.service": ("s",),
    },
    alias_groups={
        ".constants": (("c", "ExamplesFlextCliConstants"),),
        ".models": (("m", "ExamplesFlextCliModels"),),
        ".protocols": (("p", "ExamplesFlextCliProtocols"),),
        ".typings": (("t", "ExamplesFlextCliTypes"),),
        ".utilities": (("u", "ExamplesFlextCliUtilities"),),
    },
)

__all__ = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
