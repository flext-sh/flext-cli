# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.fixtures package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.fixtures.process_deadline_holder import (
        TestsFlextCliProcessDeadlineHolder,
    )


__all__: tuple[str, ...] = ("TestsFlextCliProcessDeadlineHolder",)

install_lazy_exports(
    __name__,
    globals(),
    {"TestsFlextCliProcessDeadlineHolder": ".process_deadline_holder"},
    public_exports=__all__,
)
