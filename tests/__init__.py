"""FLEXT CLI Tests - Test infrastructure and utilities.

Provides TestsCli classes extending FlextTests and FlextCli for comprehensive testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from flext_cli.models import FlextCliModels as m
    from tests.base import TestsCliServiceBase, s
    from tests.constants import TestsFlextCliConstants, TestsFlextCliConstants as c
    from tests.models import TestsFlextCliModels, tm
    from tests.protocols import TestsCliProtocols, TestsCliProtocols as p
    from tests.typings import TestsCliTypes, TestsCliTypes as t, tt
    from tests.utilities import TestsCliUtilities, TestsCliUtilities as u
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestsCliProtocols": ("tests.protocols", "TestsCliProtocols"),
    "TestsCliServiceBase": ("tests.base", "TestsCliServiceBase"),
    "TestsCliTypes": ("tests.typings", "TestsCliTypes"),
    "TestsCliUtilities": ("tests.utilities", "TestsCliUtilities"),
    "TestsFlextCliConstants": ("tests.constants", "TestsFlextCliConstants"),
    "TestsFlextCliModels": ("tests.models", "TestsFlextCliModels"),
    "c": ("tests.constants", "TestsFlextCliConstants"),
    "m": ("flext_cli", "m"),
    "p": ("tests.protocols", "TestsCliProtocols"),
    "s": ("tests.base", "s"),
    "t": ("tests.typings", "TestsCliTypes"),
    "tm": ("tests.models", "tm"),
    "tt": ("tests.typings", "tt"),
    "u": ("tests.utilities", "TestsCliUtilities"),
}
__all__ = [
    "TestsCliProtocols",
    "TestsCliServiceBase",
    "TestsCliTypes",
    "TestsCliUtilities",
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "c",
    "m",
    "p",
    "s",
    "t",
    "tm",
    "tt",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
