"""Utilities for flext-cli tests.

Provides TestsCliUtilities, extending FlextTestsUtilities with flext-cli-specific
utilities. All generic test utilities come from flext_tests.

Architecture:
- FlextTestsUtilities (flext_tests) = Generic utilities for all FLEXT projects
- TestsCliUtilities (tests/) = flext-cli-specific utilities extending FlextTestsUtilities

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.utilities import FlextTestsUtilities


class TestsCliUtilities(FlextTestsUtilities):
    """Utilities for flext-cli tests - extends FlextTestsUtilities.

    Architecture: Extends FlextTestsUtilities with flext-cli-specific utility
    definitions. All generic utilities from FlextTestsUtilities are available
    through inheritance.

    Rules:
    - NEVER redeclare utilities from FlextTestsUtilities
    - Only flext-cli-specific utilities allowed
    - All generic utilities come from FlextTestsUtilities
    """

    # NOTE: FlextTestsUtilities extends FlextUtilities and provides:
    # - Result: assert_success, assert_failure, assert_success_with_value, etc.
    # - TestContext: temporary_attribute context manager
    # - Factory: create_result, create_test_data
    # - ModelTestHelpers, RegistryHelpers, ConfigHelpers
    # - All FlextUtilities classes via inheritance
    #
    # These are available through inheritance.

    # Expose u classes through composition
    # No Cli subclass available in u


# Short alias per FLEXT convention
u = TestsCliUtilities

__all__ = [
    "TestsCliUtilities",
    "u",
]
