# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for yaml.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._yaml.convert import FlextCliUtilitiesYamlConvert
    from flext_cli._utilities._yaml.editing import FlextCliUtilitiesYamlEditing
    from flext_cli._utilities._yaml.engine import FlextCliUtilitiesYamlEngine

__all__: tuple[str, ...] = (
    "FlextCliUtilitiesYamlConvert",
    "FlextCliUtilitiesYamlEditing",
    "FlextCliUtilitiesYamlEngine",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesYamlConvert": ".convert",
        "FlextCliUtilitiesYamlEditing": ".editing",
        "FlextCliUtilitiesYamlEngine": ".engine",
    }),
    public_exports=__all__,
)
