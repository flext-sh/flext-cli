"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_cli import p as _cli_p


class FlextCliTestProtocols(FlextTestsProtocols, _cli_p):
    """Test protocols for flext-cli."""

    class Cli(_cli_p.Cli):
        """Cli domain test protocols."""

        class Tests:
            """Test-specific protocols."""


p = FlextCliTestProtocols
__all__ = ["FlextCliTestProtocols", "p"]
