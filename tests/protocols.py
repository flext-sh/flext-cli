"""Protocol definitions for flext-cli tests.

Provides TestsCliProtocols, extending FlextTestsProtocols with flext-cli-specific
protocols. All generic test protocols come from flext_tests.

Architecture:
- FlextTestsProtocols (flext_tests) = Generic protocols for all FLEXT projects
- TestsCliProtocols (tests/) = flext-cli-specific protocols extending FlextTestsProtocols

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.protocols import FlextCliProtocols
from flext_tests.protocols import FlextTestsProtocols


class TestsCliProtocols(FlextTestsProtocols, FlextCliProtocols):
    """Protocol definitions for flext-cli tests.

    Extends both FlextTestsProtocols and FlextCliProtocols with flext-cli-specific
    protocol definitions.

    Provides access to:
    - tp.Tests.Docker.* (from FlextTestsProtocols)
    - tp.Tests.Factory.* (from FlextTestsProtocols)
    - tp.Cli.* (from FlextCliProtocols)

    Rules:
    - NEVER redeclare protocols from parent classes
    - Only flext-cli-specific test protocols allowed
    """

    class Tests:
        """Project-specific test protocols.

        Extends FlextTestsProtocols.Tests with flext-cli-specific protocols.
        """

        class Cli:
            """Flext-cli-specific test protocols."""


# Runtime aliases
p = TestsCliProtocols
tp = TestsCliProtocols

__all__ = [
    "TestsCliProtocols",
    "p",
    "tp",
]
