"""Service base for flext-cli tests.

Provides TestsCliServiceBase, extending FlextTestsServiceBase and FlextService with test-specific service
functionality for test infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import s as flext_tests_s

from flext_cli import s as flext_cli_s


class TestsCliServiceBase(flext_tests_s, flext_cli_s):
    """Service base for flext-cli tests - extends FlextTestsServiceBase and FlextCliServiceBase.

    Architecture: Extends FlextTestsServiceBase and FlextCliServiceBase with test-specific service functionality.
    All base service functionality from FlextService is available through inheritance.
    """


__all__ = ["TestsCliServiceBase", "s"]

# Alias for simplified usage
s = TestsCliServiceBase
