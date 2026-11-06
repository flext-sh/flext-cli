# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.test_config_document_ingress import (
        TestsFlextCliConfigDocumentIngress,
    )


__all__: tuple[str, ...] = ("TestsFlextCliConfigDocumentIngress",)

install_lazy_exports(
    __name__,
    globals(),
    {"TestsFlextCliConfigDocumentIngress": ".test_config_document_ingress"},
    public_exports=__all__,
)
