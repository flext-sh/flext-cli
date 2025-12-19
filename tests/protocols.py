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

from flext_tests.protocols import FlextTestsProtocols

from flext_cli.protocols import FlextCliProtocols


class TestsCliProtocols(FlextTestsProtocols, FlextCliProtocols):
    """Protocol definitions for flext-cli tests - extends FlextTestsProtocols and FlextCliProtocols.

    Architecture: Extends both FlextTestsProtocols and FlextCliProtocols with flext-cli-specific protocol
    definitions. All generic protocols from both are available through inheritance.

    Rules:
    - NEVER redeclare protocols from FlextTestsProtocols or FlextCliProtocols
    - Only flext-cli-specific test protocols allowed
    - All generic protocols come from FlextTestsProtocols and FlextCliProtocols
    """

    # NOTE: FlextTestsProtocols already extends FlextProtocols.
    # FlextCliProtocols extends FlextProtocols.
    # All protocols are accessible through TestsCliProtocols via inheritance.
    #
    # Available protocols include:
    # - Foundation: ResultProtocol, ResultLike, ModelProtocol
    # - CLI: Display, Interactive, Command, etc.
    # - Test: All test-specific protocols
    #
    # Flext-cli-specific test protocols can be added here if needed.


# Runtime alias for simplified usage
p = TestsCliProtocols

__all__ = [
    "TestsCliProtocols",
    "p",
]
