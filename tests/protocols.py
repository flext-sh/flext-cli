"""Protocol definitions for flext-cli tests.

Provides FlextCliTestProtocols, extending FlextTestsProtocols with flext-cli-specific
protocols. All generic test protocols come from flext_tests.

Architecture:
- FlextTestsProtocols (flext_tests) = Generic protocols for all FLEXT projects
- FlextCliTestProtocols (tests/) = flext-cli-specific protocols extending FlextTestsProtocols

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_cli import FlextCliProtocols


class FlextCliTestProtocols(FlextTestsProtocols, FlextCliProtocols):
    """Protocol definitions for flext-cli tests.

    Extends both FlextTestsProtocols and FlextCliProtocols with flext-cli-specific
    protocol definitions.

    Provides access to:
    - FlextTestsProtocols.Tests.Docker.* (from FlextTestsProtocols)
    - FlextTestsProtocols.Tests.Factory.* (from FlextTestsProtocols)
    - FlextCliProtocols.Cli.* (from FlextCliProtocols)

    Rules:
    - NEVER redeclare protocols from parent classes
    - Only flext-cli-specific test protocols allowed
    """

    class Cli(FlextCliProtocols.Cli):
        """Flext-cli-specific protocol definitions for testing.

        Inherits all CLI protocols from FlextCliProtocols.Cli.
        Add any test-specific CLI protocols here if needed.
        """

        class Tests:
            """Test-specific protocols."""


p = FlextCliTestProtocols
__all__ = ["FlextCliTestProtocols", "p"]
