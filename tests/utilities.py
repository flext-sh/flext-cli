"""Utilities for flext-cli tests.

Provides FlextCliTestUtilities, extending FlextCliUtilities with test-specific helpers.
All source utilities come from FlextCliUtilities, test utilities from FlextTestsUtilities.

Architecture:
- FlextCliUtilities (src/) = CLI-specific utilities
- FlextTestsUtilities (flext_tests) = Generic test utilities for all FLEXT projects
- FlextCliTestUtilities (tests/) = Combined utilities for flext-cli tests

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_cli import FlextCliUtilities


class FlextCliTestUtilities(FlextCliUtilities, FlextTestsUtilities):
    """Utilities for flext-cli tests - extends both FlextCliUtilities and FlextTestsUtilities.

    Architecture: Multiple inheritance from both source utilities (FlextCliUtilities)
    and test utilities (FlextTestsUtilities).

    Inheritance Order:
    - FlextCliUtilities: CLI-specific namespaces (Cli.CliValidation, Cli.TypeNormalizer, etc.)
    - FlextTestsUtilities: Generic test utilities (Result, TestContext, Factory, etc.)

    All utilities are available through inheritance.
    """

    class Cli(FlextCliUtilities.Cli):
        """CLI-specific utilities for testing.

        Inherits all CLI utilities from FlextCliUtilities.Cli.
        Add any test-specific CLI utilities here if needed.
        """

        class Tests:
            """Test-specific utilities."""


u = FlextCliTestUtilities
__all__ = ["FlextCliTestUtilities", "u"]
