"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_cli import p


class TestsFlextCliProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-cli."""

    class Cli(p.Cli):
        """Cli domain test protocols."""

        class Tests:
            """Test-specific protocols."""


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
