# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Models package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from flext_cli._models.base import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextCliModelsBase": "flext_cli._models.base",
    "base": "flext_cli._models.base",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
