"""Test utilities for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_cli import FlextCliUtilities


class FlextCliTestUtilities(FlextTestsUtilities, FlextCliUtilities):
    """Test utilities for flext-cli."""

    class Cli(FlextCliUtilities.Cli):
        """Cli domain test utilities."""

        class Tests:
            """Test-specific utilities."""


u = FlextCliTestUtilities
__all__ = ["FlextCliTestUtilities", "u"]
