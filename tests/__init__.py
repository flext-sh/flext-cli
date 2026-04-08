# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

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
_LAZY_IMPORTS = merge_lazy_imports(
    ("tests.unit",),
    {
        "TestsFlextCliConstants": ("tests.constants", "TestsFlextCliConstants"),
        "TestsFlextCliModels": ("tests.models", "TestsFlextCliModels"),
        "TestsFlextCliProtocols": ("tests.protocols", "TestsFlextCliProtocols"),
        "TestsFlextCliTypes": ("tests.typings", "TestsFlextCliTypes"),
        "TestsFlextCliUtilities": ("tests.utilities", "TestsFlextCliUtilities"),
        "c": ("tests.constants", "TestsFlextCliConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("tests.models", "TestsFlextCliModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "TestsFlextCliProtocols"),
        "protocols": "tests.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "t": ("tests.typings", "TestsFlextCliTypes"),
        "typings": "tests.typings",
        "u": ("tests.utilities", "TestsFlextCliUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("logger", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
    "c",
    "conftest",
    "constants",
    "d",
    "e",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "t",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
