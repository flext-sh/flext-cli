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
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("ExamplesFlextCliConstants",),
        ".models": ("ExamplesFlextCliModels",),
        ".protocols": ("ExamplesFlextCliProtocols",),
        ".typings": ("ExamplesFlextCliTypes",),
        ".utilities": ("ExamplesFlextCliUtilities",),
    },
    alias_groups={
        ".constants": (("c", "ExamplesFlextCliConstants"),),
        ".models": (("m", "ExamplesFlextCliModels"),),
        ".protocols": (("p", "ExamplesFlextCliProtocols"),),
        ".typings": (("t", "ExamplesFlextCliTypes"),),
        ".utilities": (("u", "ExamplesFlextCliUtilities"),),
        "flext_core.decorators": (("d", "FlextDecorators"),),
        "flext_core.exceptions": (("e", "FlextExceptions"),),
        "flext_core.handlers": (("h", "FlextHandlers"),),
        "flext_core.mixins": (("x", "FlextMixins"),),
        "flext_core.result": (("r", "FlextResult"),),
        "flext_core.service": (("s", "FlextService"),),
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
