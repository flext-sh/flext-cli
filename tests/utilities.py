"""Utilities for flext-cli tests.

Provides TestsCliUtilities, extending FlextCliUtilities with test-specific helpers.
All source utilities come from FlextCliUtilities, test utilities from u.

Architecture:
- FlextCliUtilities (src/) = CLI-specific utilities
- u (flext_tests) = Generic test utilities for all FLEXT projects
- TestsCliUtilities (tests/) = Combined utilities for flext-cli tests

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import u

from flext_cli import FlextCliUtilities


class TestsCliUtilities(FlextCliUtilities, u):
    """Utilities for flext-cli tests - extends both FlextCliUtilities and u.

    Architecture: Multiple inheritance from both source utilities (FlextCliUtilities)
    and test utilities (u).

    Inheritance Order:
    - FlextCliUtilities: CLI-specific namespaces (Cli.CliValidation, Cli.TypeNormalizer, etc.)
    - u: Generic test utilities (Result, TestContext, Factory, etc.)

    All utilities are available through inheritance.
    """


__all__ = ["TestsCliUtilities", "u"]

u = TestsCliUtilities
