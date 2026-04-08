# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.constants import TestsFlextCliConstants, TestsFlextCliConstants as c
    from tests.models import TestsFlextCliModels, TestsFlextCliModels as m
    from tests.protocols import TestsFlextCliProtocols, TestsFlextCliProtocols as p
    from tests.typings import TestsFlextCliTypes, TestsFlextCliTypes as t
    from tests.utilities import TestsFlextCliUtilities, TestsFlextCliUtilities as u
_LAZY_IMPORTS = {
    "TestsFlextCliConstants": ("tests.constants", "TestsFlextCliConstants"),
    "TestsFlextCliModels": ("tests.models", "TestsFlextCliModels"),
    "TestsFlextCliProtocols": ("tests.protocols", "TestsFlextCliProtocols"),
    "TestsFlextCliTypes": ("tests.typings", "TestsFlextCliTypes"),
    "TestsFlextCliUtilities": ("tests.utilities", "TestsFlextCliUtilities"),
    "c": ("tests.constants", "TestsFlextCliConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.models", "TestsFlextCliModels"),
    "p": ("tests.protocols", "TestsFlextCliProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.typings", "TestsFlextCliTypes"),
    "u": ("tests.utilities", "TestsFlextCliUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
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
