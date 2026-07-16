"""Type facade for flext-cli tests.

`TestsFlextCliTypes` composes `FlextTestsTypes + t` via MRO.
`t.Tests.*` extends `FlextTestsTypes.Tests.*` with flext-cli-only test
type aliases.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes

from flext_cli import p, t


class TestsFlextCliTypes(FlextTestsTypes, t):
    """MRO facade exposing both flext-tests and flext-cli type namespaces."""

    class Tests(FlextTestsTypes.Tests):
        """Test-specific type aliases for flext-cli."""

        type OptionalStringAlias = str | None
        type StringListAlias = list[str]


t = TestsFlextCliTypes

__all__: list[str] = ["TestsFlextCliTypes", "t"]
