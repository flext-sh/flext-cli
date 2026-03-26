"""FLEXT CLI Test Helpers - Factories and utilities for test code reduction.

Provides reusable factories, validators, and helpers to reduce test code
through DRY principles and parametrized test patterns.

Extends src modules via inheritance:
- TestModels extends FlextCliModels
- TestTypes extends FlextCliTypes
- TestUtilities extends u
- TestConstants extends FlextCliConstants
- TestProtocols extends FlextCliProtocols

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests import c, m, p, t, u
    from tests._helpers import CommandsFactory
    from tests.helpers._impl import (
        FlextCliTestHelpers,
        TestScenario,
        _is_json_dict,
        _is_json_list,
    )
_LAZY_IMPORTS: Mapping[str, tuple[str, str]] = {
    "CommandsFactory": ("tests._helpers", "CommandsFactory"),
    "FlextCliTestHelpers": ("tests.helpers._impl", "FlextCliTestHelpers"),
    "TestScenario": ("tests.helpers._impl", "TestScenario"),
    "_is_json_dict": ("tests.helpers._impl", "_is_json_dict"),
    "_is_json_list": ("tests.helpers._impl", "_is_json_list"),
    "c": ("tests", "c"),
    "m": ("tests", "m"),
    "p": ("tests", "p"),
    "t": ("tests", "t"),
    "u": ("tests", "u"),
}
__all__ = [
    "CommandsFactory",
    "FlextCliTestHelpers",
    "TestScenario",
    "_is_json_dict",
    "_is_json_list",
    "c",
    "m",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
