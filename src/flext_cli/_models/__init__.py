# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Models package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_cli._models import base
    from flext_cli._models.base import FlextCliModelsBase
    from flext_core import FlextTypes

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextCliModelsBase": "flext_cli._models.base",
    "base": "flext_cli._models.base",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
