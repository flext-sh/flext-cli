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

from tests import c, m, p, t, u
from tests._helpers import CommandsFactory
from tests.helpers._impl import (
    ConfigFactory,
    FlextCliTestHelpers,
    ParamsFactory,
    TestScenario,
    ValidationHelper,
)

__all__ = [
    "CommandsFactory",
    "ConfigFactory",
    "FlextCliTestHelpers",
    "ParamsFactory",
    "TestScenario",
    "ValidationHelper",
    "c",
    "m",
    "p",
    "t",
    "u",
]
