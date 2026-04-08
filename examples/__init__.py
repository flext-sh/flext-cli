# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

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
_LAZY_IMPORTS = {
    "ExamplesFlextCliConstants": ".constants",
    "ExamplesFlextCliModels": ".models",
    "ExamplesFlextCliProtocols": ".protocols",
    "ExamplesFlextCliTypes": ".typings",
    "ExamplesFlextCliUtilities": ".utilities",
    "c": (".constants", "ExamplesFlextCliConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": (".models", "ExamplesFlextCliModels"),
    "p": (".protocols", "ExamplesFlextCliProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": (".typings", "ExamplesFlextCliTypes"),
    "u": (".utilities", "ExamplesFlextCliUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

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
