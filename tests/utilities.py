"""Utilities for flext-cli tests.

Provides TestsCliUtilities, extending FlextCliUtilities with test-specific helpers.
All source utilities come from FlextCliUtilities, test utilities from FlextTestsUtilities.

Architecture:
- FlextCliUtilities (src/) = CLI-specific utilities
- FlextTestsUtilities (flext_tests) = Generic test utilities for all FLEXT projects
- TestsCliUtilities (tests/) = Combined utilities for flext-cli tests

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.utilities import FlextCliUtilities
from flext_tests.utilities import FlextTestsUtilities


class TestsCliUtilities(FlextCliUtilities, FlextTestsUtilities):
    """Utilities for flext-cli tests - extends both FlextCliUtilities and FlextTestsUtilities.

    Architecture: Multiple inheritance from both source utilities (FlextCliUtilities)
    and test utilities (FlextTestsUtilities).

    Inheritance Order:
    - FlextCliUtilities: CLI-specific namespaces (Cli.CliValidation, Cli.TypeNormalizer, etc.)
    - FlextTestsUtilities: Generic test utilities (Result, TestContext, Factory, etc.)

    All utilities are available through inheritance.
    """

    # Exposes from FlextCliUtilities:
    # - Cli.CliValidation: CLI-specific validation
    # - Cli.TypeNormalizer: Type normalization for Typer
    # - Cli.Environment: Environment detection
    # - Cli.ConfigOps: Configuration operations
    # - Cli.FileOps: File operations
    #
    # Exposes from FlextTestsUtilities:
    # - Result: assert_success, assert_failure, etc.
    # - TestContext: temporary_attribute context manager
    # - Factory: create_result, create_test_data
    # - ModelTestHelpers, RegistryHelpers, ConfigHelpers

    # Root-level aliases for convenience (matches test expectations)
    TypeNormalizer = FlextCliUtilities.Cli.TypeNormalizer
    CliValidation = FlextCliUtilities.Cli.CliValidation
    Environment = FlextCliUtilities.Cli.Environment
    ConfigOps = FlextCliUtilities.Cli.ConfigOps
    FileOps = FlextCliUtilities.Cli.FileOps


# Short alias per FLEXT convention
u = TestsCliUtilities

__all__ = [
    "TestsCliUtilities",
    "u",
]
