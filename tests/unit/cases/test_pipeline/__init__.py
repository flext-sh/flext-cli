# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit.cases.test Pipeline package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.cases.test_pipeline.testsflextclipipelinehandlers import (
        TestsFlextCliPipelineHandlers,
    )


__all__: tuple[str, ...] = ("TestsFlextCliPipelineHandlers",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextCliPipelineHandlers": ".testsflextclipipelinehandlers",
    }),
    public_exports=__all__,
)
