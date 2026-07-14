# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Typings package."""

from __future__ import annotations

from typing import TYPE_CHECKING

# mro-i6nq.10: The package consumes its manifest's public-export contract.
from flext_cli._typings.__unit__ import PUBLIC_EXPORTS as _PUBLIC_EXPORTS
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._typings.base import FlextCliTypesBase as FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain as FlextCliTypesDomain
    from flext_cli._typings.pipeline import (
        FlextCliTypesPipeline as FlextCliTypesPipeline,
    )
    from flext_cli._typings.xlsx import FlextCliTypesXlsx as FlextCliTypesXlsx

    # mro-i6nq.10: Static declaration mirrors the installer-owned runtime binding.
    __all__: tuple[str, ...]


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)


# mro-i6nq.10: The installer publishes __all__ from the manifest's literal ABI.
install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=_PUBLIC_EXPORTS)
