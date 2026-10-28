# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for prompts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services._prompts.support import FlextCliServicesPromptsSupport

__all__: tuple[str, ...] = ("FlextCliServicesPromptsSupport",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliServicesPromptsSupport": ".support",
    }),
    public_exports=__all__,
)
