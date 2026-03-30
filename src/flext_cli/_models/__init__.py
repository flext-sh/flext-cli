# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Models package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._models import base as base
    from flext_cli._models.base import FlextCliModelsBase as FlextCliModelsBase

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextCliModelsBase": ["flext_cli._models.base", "FlextCliModelsBase"],
    "base": ["flext_cli._models.base", ""],
}

_EXPORTS: Sequence[str] = [
    "FlextCliModelsBase",
    "base",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
