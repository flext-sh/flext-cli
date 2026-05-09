"""Type facade for flext-cli tests.

`TestsFlextCliTypes` composes `FlextTestsTypes + t` via MRO.
No flext-cli-specific test types currently — `t.Tests.*` resolves to
`FlextTestsTypes.Tests.*` automatically. Add nested classes here only
when a flext-cli-only test type appears.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes

from flext_cli import t


class TestsFlextCliTypes(FlextTestsTypes, t):
    """MRO facade exposing both flext-tests and flext-cli type namespaces."""


t = TestsFlextCliTypes

__all__: list[str] = ["TestsFlextCliTypes", "t"]
