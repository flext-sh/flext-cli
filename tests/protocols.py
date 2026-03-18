"""Protocol definitions for flext-cli tests.

Provides TestsCliProtocols, extending p with flext-cli-specific
protocols. All generic test protocols come from flext_tests.

Architecture:
- p (flext_tests) = Generic protocols for all FLEXT projects
- TestsCliProtocols (tests/) = flext-cli-specific protocols extending p

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import p

from flext_cli import FlextCliProtocols


class TestsCliProtocols(p, FlextCliProtocols):
    """Protocol definitions for flext-cli tests.

    Extends both p and FlextCliProtocols with flext-cli-specific
    protocol definitions.

    Provides access to:
    - p.Tests.Docker.* (from p)
    - p.Tests.Factory.* (from p)
    - p.Cli.* (from FlextCliProtocols)

    Rules:
    - NEVER redeclare protocols from parent classes
    - Only flext-cli-specific test protocols allowed
    """


__all__ = ["TestsCliProtocols", "p"]

p = TestsCliProtocols
